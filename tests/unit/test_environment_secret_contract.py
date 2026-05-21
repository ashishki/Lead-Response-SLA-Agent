from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lead_sla_agent.config import (
    API_SECRET_NAMES,
    DEPLOY_SECRET_NAMES,
    PROVIDER_SECRET_NAMES_BY_ADAPTER,
    SECRET_REDACTION,
    WORKER_SECRET_NAMES,
    MissingRequiredSecretError,
    redact_secret_value,
    required_secret_names,
    validate_required_secrets,
)


def test_required_secrets_are_partitioned_by_environment_and_runtime() -> None:
    assert required_secret_names("local", "api") == API_SECRET_NAMES
    assert required_secret_names("local", "worker") == WORKER_SECRET_NAMES
    assert required_secret_names("local", "deploy") == frozenset()
    assert required_secret_names("staging", "deploy") == frozenset(
        {"STAGING_VPS_HOST", "STAGING_VPS_USER", "STAGING_VPS_SSH_KEY"}
    )
    assert required_secret_names("production", "deploy") == frozenset(
        {"PRODUCTION_VPS_HOST", "PRODUCTION_VPS_USER", "PRODUCTION_VPS_SSH_KEY"}
    )
    assert (
        required_secret_names("staging", "deploy") | required_secret_names("production", "deploy")
        == DEPLOY_SECRET_NAMES
    )


def test_missing_secret_failure_lists_names_without_values() -> None:
    with pytest.raises(MissingRequiredSecretError) as exc_info:
        validate_required_secrets(
            app_env="production",
            runtime="deploy",
            environ={
                "PRODUCTION_VPS_HOST": "prod.example.test",
                "PRODUCTION_VPS_USER": "deploy",
            },
        )

    message = str(exc_info.value)
    assert message == "missing required secrets: PRODUCTION_VPS_SSH_KEY"
    assert "prod.example.test" not in message
    assert "deploy" not in message
    assert redact_secret_value("real-secret-value") == SECRET_REDACTION


def test_provider_credentials_are_scoped_per_adapter() -> None:
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["email"] == frozenset(
        {"EMAIL_API_KEY", "EMAIL_SENDER", "EMAIL_API_URL"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["postmark_email"] == frozenset(
        {"POSTMARK_SERVER_TOKEN", "POSTMARK_SENDER", "POSTMARK_MESSAGE_STREAM"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["twilio_whatsapp"] == frozenset(
        {"TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["telegram_bot"] == frozenset({"TELEGRAM_BOT_TOKEN"})
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["calendar"] == frozenset(
        {"CALENDAR_API_TOKEN", "CALENDAR_API_URL"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["crm"] == frozenset({"CRM_API_TOKEN", "CRM_API_URL"})
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["embedding"] == frozenset(
        {"EMBEDDING_API_KEY", "EMBEDDING_MODEL", "EMBEDDING_DIMENSIONS", "EMBEDDING_API_URL"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["email"].isdisjoint(
        PROVIDER_SECRET_NAMES_BY_ADAPTER["crm"]
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["calendar"].isdisjoint(
        PROVIDER_SECRET_NAMES_BY_ADAPTER["email"]
    )


def test_runbook_documents_local_staging_production_and_rotation_revocation() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    for required in (
        "Local required secrets",
        "Staging required secrets",
        "Production required secrets",
        "Provider adapter scopes",
        "STAGING_VPS_HOST",
        "PRODUCTION_VPS_SSH_KEY",
        "Verify revocation by making a negative smoke call",
    ):
        assert required in content


def test_deploy_workflow_validates_secret_names_without_printing_values() -> None:
    workflow_text = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    staging_steps = {
        step["name"]: step for step in workflow["jobs"]["staging_deploy"]["steps"] if "name" in step
    }
    production_steps = {
        step["name"]: step
        for step in workflow["jobs"]["production_deploy"]["steps"]
        if "name" in step
    }

    assert "Validate staging deploy secret names" in staging_steps
    assert "Validate staging runtime secret names" in staging_steps
    assert "Validate production deploy secret names" in production_steps
    assert "Validate production runtime secret names" in production_steps
    assert 'test -n "$STAGING_VPS_SSH_KEY"' in workflow_text
    assert 'test -n "$PRODUCTION_VPS_SSH_KEY"' in workflow_text
    assert "grep -q '^EMAIL_API_KEY=' .env" in workflow_text
    assert 'printf "$SSH_PRIVATE_KEY"' not in workflow_text
