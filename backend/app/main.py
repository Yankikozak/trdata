from datetime import date, timedelta
import json
from typing import Literal

import httpx
from fastapi import FastAPI, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.concurrency import run_in_threadpool
from starlette.status import HTTP_307_TEMPORARY_REDIRECT

from app.analytics.risk import historical_var, max_drawdown, parametric_var, sharpe_ratio
from app.core.config import get_settings
from app.providers.bist_data import BISTDataProvider
from app.providers.market_data import DemoMarketDataProvider, YahooFinanceProvider

settings = get_settings()
market_provider = YahooFinanceProvider()
bist_provider = BISTDataProvider()
app = FastAPI(title=settings.app_name, version="0.1.0", description="BIST analytics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def demo_snapshot() -> dict:
    return {
        "symbol": "XU100",
        "value": 10342.18,
        "change": 1.84,
        "volume": "128.4B TL",
        "as_of": "Demo data | 27 Sep 2026",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


@app.get("/api/market/summary", include_in_schema=False)
def legacy_market_redirect() -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url}/", status_code=HTTP_307_TEMPORARY_REDIRECT)


@app.get("/api/stocks/{symbol}", include_in_schema=False)
def legacy_stock_redirect(symbol: str) -> RedirectResponse:
    safe_symbol = symbol.strip().upper()
    return RedirectResponse(f"{settings.frontend_url}/stocks/{safe_symbol}", status_code=HTTP_307_TEMPORARY_REDIRECT)


@app.get("/api/macro", include_in_schema=False)
def legacy_macro_redirect() -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url}/macro", status_code=HTTP_307_TEMPORARY_REDIRECT)


@app.get("/api/v1/market/summary")
async def market_summary() -> dict:
    symbols = ["ASELS", "THYAO", "EREGL", "KCHOL"]
    try:
        quotes = [await market_provider.latest(symbol) for symbol in symbols]
        index = await market_provider.latest("XU100")
        usd_try = await market_provider.latest("TRY=X")
        brent = await market_provider.latest("BZ=F")
        return {
            "demo": False,
            "source": "Yahoo Finance delayed feed",
            "index": {**index, "value": index["price"], "as_of": "Yahoo Finance delayed feed"},
            "movers": [{"symbol": q["symbol"], "name": q["symbol"], "change": round(q["change"], 2), "price": q["price"]} for q in quotes],
            "sectors": [],
            "macro": [
                {"label": "USD/TRY", "value": f"{usd_try['price']:.2f}", "trend": "up"},
                {"label": "Brent", "value": f"${brent['price']:.2f}", "trend": "up"},
            ],
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        pass
    return {
        "demo": True,
        "index": demo_snapshot(),
        "movers": [
            {"symbol": "ASELS", "name": "Aselsan", "change": 6.42, "price": 68.55},
            {"symbol": "THYAO", "name": "Türk Hava Yolları", "change": 4.17, "price": 312.4},
            {"symbol": "EREGL", "name": "Ereğli Demir Çelik", "change": -3.18, "price": 54.2},
            {"symbol": "KCHOL", "name": "Koç Holding", "change": -2.46, "price": 198.9},
        ],
        "sectors": [
            {"name": "Bankacılık", "change": 2.8, "weight": 24},
            {"name": "Holding", "change": 1.6, "weight": 18},
            {"name": "Ulaştırma", "change": 3.9, "weight": 11},
            {"name": "Metal", "change": -1.1, "weight": 9},
            {"name": "Teknoloji", "change": 0.7, "weight": 7},
            {"name": "Enerji", "change": -2.2, "weight": 8},
        ],
        "macro": [
            {"label": "Politika faizi", "value": "%46.00", "trend": "stable"},
            {"label": "TÜFE yıllık", "value": "%39.20", "trend": "down"},
            {"label": "USD/TRY", "value": "41.18", "trend": "up"},
            {"label": "Brent", "value": "$71.40", "trend": "up"},
        ],
    }


@app.get("/api/v1/bist/universe")
def bist_universe(refresh: bool = False) -> dict:
    symbols = bist_provider.symbols(refresh=refresh)
    return {"exchange": "BIST / IST", "count": len(symbols), "symbols": symbols, "errors": bist_provider.last_errors}


@app.get("/api/v1/bist/prices")
async def bist_prices(
    start: date,
    end: date,
    symbols: str | None = Query(default=None, description="Comma-separated BIST symbols; omit to download the full universe"),
    interval: Literal["1d", "1wk", "1mo"] = "1d",
) -> dict:
    requested_symbols = symbols.split(",") if symbols else None
    frame = await run_in_threadpool(bist_provider.historical_prices, start, end, requested_symbols, interval)
    records = json.loads(frame.to_json(orient="records", date_format="iso"))
    return {
        "exchange": "BIST / IST",
        "interval": interval,
        "symbols_requested": requested_symbols or bist_provider.symbols(),
        "rows": len(records),
        "columns": list(frame.columns),
        "prices": records,
        "errors": bist_provider.last_errors,
    }


@app.get("/api/v1/stocks/{symbol}/risk")
def stock_risk(symbol: str) -> dict:
    returns = [0.012, -0.008, 0.004, 0.017, -0.011, 0.006, 0.002, -0.004, 0.009, -0.007]
    prices = [100, 101.2, 100.4, 100.8, 102.5, 101.4, 102, 102.2, 101.8, 102.7, 102]
    return {
        "symbol": symbol.upper(),
        "demo": True,
        "var_95": round(historical_var(returns) * 100, 2),
        "var_99": round(parametric_var(returns, 0.99) * 100, 2),
        "sharpe": round(sharpe_ratio(returns), 2),
        "max_drawdown": round(max_drawdown(prices) * 100, 2),
        "beta_bist100": 1.08,
        "altman_z_score": 3.42,
    }


@app.get("/api/v1/stocks/{symbol}/prices")
async def stock_prices(symbol: str, period: Literal["day", "month", "year"] = "month") -> dict:
    end = date.today()
    try:
        points = await market_provider.history(symbol.upper(), period)
        return {"symbol": symbol.upper(), "demo": False, "source": "Yahoo Finance delayed feed", "prices": points}
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        points = await DemoMarketDataProvider().daily_prices(symbol.upper(), end - timedelta(days=90), end)
        return {"symbol": symbol.upper(), "demo": True, "source": "Synthetic demo fallback", "prices": points}


@app.websocket("/ws/market/{symbol}")
async def market_stream(websocket: WebSocket, symbol: str) -> None:
    await websocket.accept()
    await websocket.send_json({"symbol": symbol.upper(), "demo": True, "status": "connected"})
    await websocket.close()
