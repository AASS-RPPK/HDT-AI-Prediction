from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PORT: int = Field(default=8000, ge=1, le=65535)
    DATABASE_URL: str

    # Redis URL used as Celery broker and result backend.
    REDIS_URL: str = "redis://redis:6379/0"

    # Comma-separated allowed origins for CORS.
    CORS_ORIGINS: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _normalize_cors_origins(cls, v: object) -> str:
        if v is None:
            return ""
        return str(v)

    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if not raw:
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
