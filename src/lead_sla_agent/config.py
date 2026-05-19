"""Application settings loaded from the process environment."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings required by the Phase 1 service skeleton."""

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_env: str = Field(default="test", validation_alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+asyncpg://lead_test:lead_test@localhost:5432/lead_sla_test",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    secret_key: str = Field(default="test-secret-key", validation_alias="SECRET_KEY")
    webhook_shared_secret: str = Field(
        default="test-webhook-secret",
        validation_alias="WEBHOOK_SHARED_SECRET",
    )


def get_settings() -> Settings:
    """Create settings from the current environment."""
    return Settings()
