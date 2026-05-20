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
    operator_auth_secret: str = Field(
        default="test-operator-auth-secret",
        validation_alias="OPERATOR_AUTH_SECRET",
    )
    webhook_shared_secret: str = Field(
        default="test-webhook-secret",
        validation_alias="WEBHOOK_SHARED_SECRET",
    )
    email_api_key: str = Field(default="test-email-key", validation_alias="EMAIL_API_KEY")
    email_sender: str = Field(default="leads@example.test", validation_alias="EMAIL_SENDER")
    email_api_url: str = Field(
        default="https://email-provider.example.test/messages",
        validation_alias="EMAIL_API_URL",
    )
    calendar_api_token: str = Field(
        default="test-calendar-token",
        validation_alias="CALENDAR_API_TOKEN",
    )
    calendar_api_url: str = Field(
        default="https://calendar-provider.example.test",
        validation_alias="CALENDAR_API_URL",
    )
    crm_api_token: str = Field(default="test-crm-token", validation_alias="CRM_API_TOKEN")
    crm_api_url: str = Field(
        default="https://crm-provider.example.test",
        validation_alias="CRM_API_URL",
    )
    embedding_api_key: str = Field(
        default="test-embedding-key",
        validation_alias="EMBEDDING_API_KEY",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="EMBEDDING_MODEL",
    )
    embedding_dimensions: int = Field(default=1536, validation_alias="EMBEDDING_DIMENSIONS")
    embedding_api_url: str = Field(
        default="https://api.openai.com/v1/embeddings",
        validation_alias="EMBEDDING_API_URL",
    )


def get_settings() -> Settings:
    """Create settings from the current environment."""
    return Settings()
