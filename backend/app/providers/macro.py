import os
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")


class EVDSProvider:
    """TCMB EVDS adapter using the server-side EVDS_API_KEY from .env."""

    base_url = "https://evds2.tcmb.gov.tr/service/evds"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("EVDS_API_KEY")

    async def series(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        if not self.api_key:
            raise RuntimeError("EVDS_API_KEY is not configured in the server environment")

        params = {
            "type": "json",
            "key": self.api_key,
        }
        if start_date:
            params["startDate"] = start_date.strftime("%d-%m-%Y")
        if end_date:
            params["endDate"] = end_date.strftime("%d-%m-%Y")

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}/series={code}", params=params)
            response.raise_for_status()
            if "json" not in response.headers.get("content-type", "").lower():
                raise RuntimeError(
                    f"EVDS returned a non-JSON response from {response.url.host}; check the current EVDS API endpoint"
                )
            payload = response.json()

        items = payload.get("items", [])
        if not isinstance(items, list):
            raise ValueError("Unexpected EVDS response: items must be a list")
        return items


class TUIKProvider:
    """Placeholder for TÜİK integration."""

    async def series(self, code: str) -> list[dict]:
        raise NotImplementedError("Configure TUIK_API_KEY and implement the licensed adapter")
