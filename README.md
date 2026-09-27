# TR-Analytix

BIST odaklı finansal veri ve analitik platformu için modüler monolith başlangıç workspace'i.

## Stack

- **API:** FastAPI, SQLAlchemy async, Pydantic Settings, Celery
- **Data:** PostgreSQL + TimescaleDB, Redis
- **UI:** Next.js App Router, TypeScript, Tailwind CSS, Lightweight Charts, Recharts, Lucide
- **Ops:** Docker Compose, health checks, environment-based configuration

## Quick start

```bash
copy .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

The dashboard now requests BIST quotes from the Yahoo Finance chart endpoint using `.IS` symbols and marks the result `LIVE / DELAYED`. This is real public market data but not an exchange-certified or guaranteed real-time feed. For production or trading decisions, replace `YahooFinanceProvider` with a licensed Borsa Istanbul provider adapter. EVDS/TUIK macro series still require their official API keys and adapter implementations.

If the API is unavailable, the UI keeps a clearly marked synthetic fallback instead of presenting demo values as live data.

## Structure

```text
backend/           FastAPI API, analytics services, Celery worker
frontend/          Next.js dashboard
infra/             TimescaleDB initialization and migrations
docker-compose.yml Local service orchestration
```

## Local development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload

cd frontend
npm install
npm run dev
```

## Quality checks

```bash
cd backend && pytest
cd frontend && npm run lint && npm run build
```

This is an implementation foundation, not a live trading terminal. Risk and econometric outputs require validated historical data, corporate-action handling, market calendars, and model governance before production use. The editor file links in generated responses open workspace files; application links such as `/risk-lab` only open after the frontend server is running.

## BIST bulk data provider

`BISTDataProvider` discovers the current Yahoo Finance Istanbul (`IST`) universe dynamically and appends `.IS` to each symbol. It downloads real OHLCV history with `yfinance` and returns a normalized Pandas DataFrame with `date`, `symbol`, `open`, `high`, `low`, `close`, `volume`, and `adj_close` columns.

```python
from datetime import date, timedelta
from app.providers.bist_data import BISTDataProvider

provider = BISTDataProvider()
symbols = provider.symbols()  # dynamically discovered BIST universe
prices = provider.historical_prices(date.today() - timedelta(days=30), date.today())
```

API endpoints:

- `GET /api/v1/bist/universe` returns the current symbol catalog.
- `GET /api/v1/bist/prices?start=2026-09-01&end=2026-09-27` downloads the full universe.
- Add `symbols=THYAO,ASELS` to request a smaller batch.

Yahoo Finance is a public delayed source and may omit suspended, newly listed, or unsupported symbols. Per-symbol failures are returned in `errors` and stored in `BISTDataProvider.last_errors` instead of aborting the whole batch.
