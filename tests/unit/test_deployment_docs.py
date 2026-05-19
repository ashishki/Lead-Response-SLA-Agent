from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED_RUNTIME_ENV = {
    "APP_ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "SECRET_KEY",
    "WEBHOOK_SHARED_SECRET",
}


def test_docker_compose_config_declares_required_services() -> None:
    compose = yaml.safe_load(Path("compose.yml").read_text(encoding="utf-8"))

    assert {"api", "worker", "postgres", "redis"} <= set(compose["services"])
    for service_name in ("api", "worker"):
        service_env = set(compose["services"][service_name]["environment"])
        assert service_env >= REQUIRED_RUNTIME_ENV


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
