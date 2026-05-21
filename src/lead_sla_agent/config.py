"""Application settings loaded from the process environment."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SECRET_REDACTION = "[secret-redacted]"

API_SECRET_NAMES = frozenset(
    {
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "OPERATOR_AUTH_SECRET",
        "WEBHOOK_SHARED_SECRET",
    }
)
WORKER_SECRET_NAMES = frozenset(
    {
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "EMAIL_API_KEY",
        "EMAIL_SENDER",
        "EMAIL_API_URL",
        "CALENDAR_API_TOKEN",
        "CALENDAR_API_URL",
        "CRM_API_TOKEN",
        "CRM_API_URL",
        "EMBEDDING_API_KEY",
        "EMBEDDING_MODEL",
        "EMBEDDING_DIMENSIONS",
        "EMBEDDING_API_URL",
        "MAX_AUTONOMOUS_TURNS",
        "MAX_TOOL_CALLS_PER_TURN",
        "MAX_INDEX_AGE_HOURS",
    }
)
DEPLOY_SECRET_NAMES = frozenset(
    {
        "STAGING_VPS_HOST",
        "STAGING_VPS_USER",
        "STAGING_VPS_SSH_KEY",
        "PRODUCTION_VPS_HOST",
        "PRODUCTION_VPS_USER",
        "PRODUCTION_VPS_SSH_KEY",
    }
)
PROVIDER_SECRET_NAMES_BY_ADAPTER = {
    "email": frozenset({"EMAIL_API_KEY", "EMAIL_SENDER", "EMAIL_API_URL"}),
    "postmark_email": frozenset(
        {"POSTMARK_SERVER_TOKEN", "POSTMARK_SENDER", "POSTMARK_MESSAGE_STREAM"}
    ),
    "twilio_whatsapp": frozenset(
        {"TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"}
    ),
    "telegram_bot": frozenset({"TELEGRAM_BOT_TOKEN"}),
    "calendar": frozenset({"CALENDAR_API_TOKEN", "CALENDAR_API_URL"}),
    "crm": frozenset({"CRM_API_TOKEN", "CRM_API_URL"}),
    "embedding": frozenset(
        {"EMBEDDING_API_KEY", "EMBEDDING_MODEL", "EMBEDDING_DIMENSIONS", "EMBEDDING_API_URL"}
    ),
}
REQUIRED_SECRETS_BY_ENVIRONMENT = {
    "local": {
        "api": API_SECRET_NAMES,
        "worker": WORKER_SECRET_NAMES,
        "deploy": frozenset[str](),
    },
    "staging": {
        "api": API_SECRET_NAMES,
        "worker": WORKER_SECRET_NAMES,
        "deploy": frozenset({"STAGING_VPS_HOST", "STAGING_VPS_USER", "STAGING_VPS_SSH_KEY"}),
    },
    "production": {
        "api": API_SECRET_NAMES,
        "worker": WORKER_SECRET_NAMES,
        "deploy": frozenset(
            {"PRODUCTION_VPS_HOST", "PRODUCTION_VPS_USER", "PRODUCTION_VPS_SSH_KEY"}
        ),
    },
}


class MissingRequiredSecretError(RuntimeError):
    """Raised when required secret names are absent without exposing values."""


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
    postmark_server_token: str = Field(
        default="test-postmark-token",
        validation_alias="POSTMARK_SERVER_TOKEN",
    )
    postmark_sender: str = Field(
        default="leads@example.test",
        validation_alias="POSTMARK_SENDER",
    )
    postmark_message_stream: str = Field(
        default="outbound",
        validation_alias="POSTMARK_MESSAGE_STREAM",
    )
    postmark_api_url: str = Field(
        default="https://api.postmarkapp.com/email",
        validation_alias="POSTMARK_API_URL",
    )
    twilio_account_sid: str = Field(
        default="test-twilio-account-sid",
        validation_alias="TWILIO_ACCOUNT_SID",
    )
    twilio_auth_token: str = Field(
        default="test-twilio-auth-token",
        validation_alias="TWILIO_AUTH_TOKEN",
    )
    twilio_whatsapp_from: str = Field(
        default="whatsapp:+15550000000",
        validation_alias="TWILIO_WHATSAPP_FROM",
    )
    twilio_api_url: str = Field(
        default="https://api.twilio.com/2010-04-01",
        validation_alias="TWILIO_API_URL",
    )
    telegram_bot_token: str = Field(
        default="test-telegram-bot-token",
        validation_alias="TELEGRAM_BOT_TOKEN",
    )
    telegram_api_url: str = Field(
        default="https://api.telegram.org",
        validation_alias="TELEGRAM_API_URL",
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


def required_secret_names(app_env: str, runtime: str) -> frozenset[str]:
    try:
        runtime_contract = REQUIRED_SECRETS_BY_ENVIRONMENT[app_env]
    except KeyError:
        raise ValueError("unsupported app environment") from None
    try:
        return runtime_contract[runtime]
    except KeyError:
        raise ValueError("unsupported runtime") from None


def validate_required_secrets(
    *,
    app_env: str,
    runtime: str,
    environ: Mapping[str, str | None],
) -> None:
    missing = sorted(
        name for name in required_secret_names(app_env, runtime) if not environ.get(name)
    )
    if missing:
        raise MissingRequiredSecretError("missing required secrets: " + ", ".join(missing))


def redact_secret_value(value: str | None) -> str:
    del value
    return SECRET_REDACTION
