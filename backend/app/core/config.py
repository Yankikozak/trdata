from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")


class Settings(BaseSettings):
    app_name: str = "TR-Analytix API"
    database_url: str = "postgresql+asyncpg://tr_analytix:change-me@localhost:5432/tr_analytix"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "local-development-secret"
    cors_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"
    evds_api_key: str | None = None
    tuik_api_key: str | None = None
    market_data_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
