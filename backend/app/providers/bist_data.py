from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import os
from typing import Iterable

import pandas as pd
import yfinance as yf
from yfinance import EquityQuery


class BISTDataProvider:
    """Batch historical OHLCV provider for all Yahoo-listed BIST equities."""

    exchange = "IST"
    batch_size = 100
    required_columns = ("open", "high", "low", "close", "volume")

    def __init__(self, symbols: Iterable[str] | None = None, catalog_path: str | Path | None = None) -> None:
        self._symbols = self._normalize_symbols(symbols) if symbols else None
        self.catalog_path = Path(catalog_path) if catalog_path else Path(__file__).with_name("bist_symbols.txt")
        self.last_errors: dict[str, str] = {}

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        cleaned = symbol.strip().upper()
        return cleaned[:-3] if cleaned.endswith(".IS") else cleaned

    @classmethod
    def _normalize_symbols(cls, symbols: Iterable[str]) -> list[str]:
        return sorted({cls._normalize_symbol(symbol) for symbol in symbols if symbol and symbol.strip()})

    @staticmethod
    def _ticker(symbol: str) -> str:
        return f"{BISTDataProvider._normalize_symbol(symbol)}.IS"

    def _load_catalog_fallback(self) -> list[str]:
        if not self.catalog_path.exists():
            return []
        return self._normalize_symbols(self.catalog_path.read_text(encoding="utf-8").splitlines())

    def symbols(self, refresh: bool = False) -> list[str]:
        """Return current BIST symbols, discovered from Yahoo with a local fallback."""
        if self._symbols is not None and not refresh:
            return self._symbols.copy()

        configured = os.getenv("BIST_SYMBOLS", "")
        if configured and not refresh:
            self._symbols = self._normalize_symbols(configured.split(","))
            return self._symbols.copy()

        try:
            query = EquityQuery("eq", ["exchange", self.exchange])
            discovered: list[str] = []
            offset = 0
            while True:
                response = yf.screen(query, offset=offset, size=250, sortField="ticker", sortAsc=True)
                quotes = response.get("quotes", [])
                discovered.extend(
                    self._normalize_symbol(quote["symbol"])
                    for quote in quotes
                    if quote.get("symbol", "").upper().endswith(".IS")
                )
                total = int(response.get("total", len(discovered)))
                offset += len(quotes)
                if not quotes or offset >= total:
                    break
            if discovered:
                self._symbols = self._normalize_symbols(discovered)
                return self._symbols.copy()
        except Exception as error:
            self.last_errors["catalog"] = f"BIST symbol discovery failed: {error}"

        self._symbols = self._load_catalog_fallback()
        if not self._symbols:
            self.last_errors["catalog"] = "No BIST symbol catalog available"
        return self._symbols.copy()

    def historical_prices(
        self,
        start: date | str,
        end: date | str,
        symbols: Iterable[str] | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Download OHLCV history and return a normalized long-format DataFrame."""
        requested = self._normalize_symbols(symbols) if symbols else self.symbols()
        columns = ["date", "symbol", *self.required_columns, "adj_close"]
        if not requested:
            return pd.DataFrame(columns=columns)

        start_date = pd.Timestamp(start).date()
        end_date = pd.Timestamp(end).date()
        end_exclusive = end_date + timedelta(days=1)
        frames: list[pd.DataFrame] = []
        self.last_errors = {key: value for key, value in self.last_errors.items() if key == "catalog"}

        for offset in range(0, len(requested), self.batch_size):
            batch = requested[offset:offset + self.batch_size]
            tickers = [self._ticker(symbol) for symbol in batch]
            try:
                raw = yf.download(
                    tickers=tickers,
                    start=start_date,
                    end=end_exclusive,
                    interval=interval,
                    auto_adjust=False,
                    group_by="column",
                    threads=True,
                    progress=False,
                )
                frames.extend(self._normalize_download(raw, batch))
            except Exception as error:
                message = str(error)
                for symbol in batch:
                    self.last_errors[symbol] = message

        if not frames:
            return pd.DataFrame(columns=columns)
        return pd.concat(frames, ignore_index=True)[columns].sort_values(["date", "symbol"]).reset_index(drop=True)

    def _normalize_download(self, raw: pd.DataFrame, symbols: list[str]) -> list[pd.DataFrame]:
        if raw.empty:
            for symbol in symbols:
                self.last_errors[symbol] = "No historical rows returned"
            return []

        frames: list[pd.DataFrame] = []
        is_multi = isinstance(raw.columns, pd.MultiIndex)
        for symbol in symbols:
            ticker = self._ticker(symbol)
            try:
                if is_multi:
                    if ticker not in raw.columns.get_level_values(-1):
                        raise KeyError(f"Ticker {ticker} missing from download response")
                    frame = raw.xs(ticker, level=-1, axis=1, drop_level=True).copy()
                else:
                    frame = raw.copy()
                frame.columns = [str(column).lower().replace(" ", "_") for column in frame.columns]
                missing = [column for column in self.required_columns if column not in frame.columns]
                if missing:
                    raise KeyError(f"Missing columns: {', '.join(missing)}")
                frame = frame.dropna(subset=list(self.required_columns), how="all")
                if frame.empty:
                    raise ValueError("No complete OHLCV rows returned")
                frame = frame.rename(columns={"adj_close": "adj_close"})
                if "adj_close" not in frame.columns:
                    frame["adj_close"] = frame["close"]
                frame.insert(0, "symbol", symbol)
                frame = frame.reset_index().rename(columns={"Date": "date", "Datetime": "date"})
                frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
                frames.append(frame[["date", "symbol", *self.required_columns, "adj_close"]])
            except Exception as error:
                self.last_errors[symbol] = str(error)
        return frames
