from datetime import date, datetime, timedelta, timezone
import time

import httpx


class MarketDataProvider:
    """Adapter boundary for a licensed BIST data provider."""

    async def daily_prices(self, symbol: str, start: date, end: date) -> list[dict]:
        raise NotImplementedError

    async def latest(self, symbol: str) -> dict:
        raise NotImplementedError


class YahooFinanceProvider(MarketDataProvider):
    """Public, delayed market-data adapter for development and research use."""

    base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    @staticmethod
    def _ticker(symbol: str) -> str:
        return symbol if any(marker in symbol for marker in ("=", "^", ".")) else f"{symbol}.IS"

    async def _chart(self, symbol: str, period1: int, period2: int, interval: str = "1d") -> dict:
        async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "TR-Analytix/0.1"}) as client:
            response = await client.get(
                f"{self.base_url}/{self._ticker(symbol)}",
                params={"period1": period1, "period2": period2, "interval": interval, "events": "div,splits"},
            )
            response.raise_for_status()
            payload = response.json()["chart"]["result"][0]
            return payload

    async def latest(self, symbol: str) -> dict:
        end = int(time.time())
        chart = await self._chart(symbol.upper(), end - 7 * 86400, end + 86400, "1d")
        meta = chart["meta"]
        price = meta.get("regularMarketPrice") or meta.get("chartPreviousClose")
        previous = meta.get("previousClose") or meta.get("chartPreviousClose") or price
        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": ((price - previous) / previous * 100) if previous else 0,
            "currency": meta.get("currency", "TRY"),
            "source": "Yahoo Finance delayed feed",
            "demo": False,
        }

    async def daily_prices(self, symbol: str, start: date, end: date) -> list[dict]:
        chart = await self._chart(
            symbol.upper(),
            int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp()),
            int(datetime.combine(end, datetime.max.time(), tzinfo=timezone.utc).timestamp()),
        )
        timestamps = chart.get("timestamp", [])
        closes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        return [
            {"time": datetime.fromtimestamp(timestamp, timezone.utc).date().isoformat(), "close": close}
            for timestamp, close in zip(timestamps, closes)
            if close is not None
        ]

    async def history(self, symbol: str, period: str) -> list[dict]:
        end = int(time.time())
        seconds, interval, label_format = {
            "day": (2 * 86400, "5m", "%H:%M"),
            "month": (32 * 86400, "1h", "%d %b"),
            "year": (366 * 86400, "1d", "%Y-%m-%d"),
        }.get(period, (32 * 86400, "1h", "%d %b"))
        chart = await self._chart(symbol.upper(), end - seconds, end + 86400, interval)
        timestamps = chart.get("timestamp", [])
        closes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        return [
            {"time": datetime.fromtimestamp(timestamp, timezone.utc).strftime(label_format), "close": close}
            for timestamp, close in zip(timestamps, closes)
            if close is not None
        ]


class DemoMarketDataProvider(MarketDataProvider):
    """Synthetic data for local UI development; never use as live market data."""

    async def daily_prices(self, symbol: str, start: date, end: date) -> list[dict]:
        points = []
        price = 100.0
        current = start
        while current <= end:
            if current.weekday() < 5:
                price *= 1 + ((hash(f"{symbol}-{current}") % 300) - 150) / 100000
                points.append({"time": current.isoformat(), "close": round(price, 2)})
            current += timedelta(days=1)
        return points

    async def latest(self, symbol: str) -> dict:
        return {"symbol": symbol.upper(), "price": 100.0, "change": 0.0, "currency": "TRY", "source": "Synthetic demo", "demo": True}
