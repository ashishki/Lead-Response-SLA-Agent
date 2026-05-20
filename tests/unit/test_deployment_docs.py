from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED_API_ENV = {
    "APP_ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "OPERATOR_AUTH_SECRET",
    "WEBHOOK_SHARED_SECRET",
}
REQUIRED_WORKER_ENV = {
    "APP_ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "EMAIL_API_KEY",
    "CALENDAR_API_TOKEN",
    "CRM_API_TOKEN",
    "EMBEDDING_API_KEY",
}


def test_docker_compose_config_declares_required_services() -> None:
    compose = yaml.safe_load(Path("compose.yml").read_text(encoding="utf-8"))

    assert {"api", "worker", "postgres", "redis"} <= set(compose["services"])
    assert set(compose["services"]["api"]["environment"]) >= REQUIRED_API_ENV
    assert set(compose["services"]["worker"]["environment"]) >= REQUIRED_WORKER_ENV


def test_runbook_contains_required_sections() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    for section in (
        "## Setup",
        "## Webhook Configuration",
        "## Seed Knowledge Ingestion",
        "## Operator Review",
        "## Rollback",
        "## Safe Handoff",
    ):
        assert section in content


def test_runbook_documents_secret_source() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "environment variables or deployment secret storage" in content
    assert "Do not commit real credentials" in content
