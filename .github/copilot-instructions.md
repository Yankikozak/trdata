# TR-Analytix Workspace Instructions

- Project: BIST-focused financial data and analytics platform.
- Backend: Python, FastAPI, async REST/WebSocket APIs, Celery workers.
- Data: PostgreSQL with TimescaleDB, Redis for cache/session/rate limits.
- Frontend: Next.js App Router, TypeScript, Tailwind CSS, Lucide React.
- Charts: Lightweight Charts for price data; Recharts for analytics.
- Use provider adapters for EVDS, TUIK and market feeds. Demo data must be clearly labeled and never presented as live market data.
- Keep secrets in environment variables; never commit API keys.
- Run focused tests/typechecks after changes and preserve existing user changes.

## Setup Checklist

- [x] Clarify project requirements
- [x] Scaffold project
- [x] Customize project
- [x] Install required extensions (none required for this scaffold)
- [ ] Compile project (blocked: Python, Node.js and Docker are unavailable in PATH)
- [ ] Create and run task
- [ ] Launch project (requires local runtime confirmation)
- [x] Ensure documentation is complete
