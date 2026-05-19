from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW_PATH = Path(".github/workflows/ci.yml")
EXPECTED_TEST_ENV = {
    "APP_ENV": "test",
    "DATABASE_URL": "postgresql+asyncpg://lead_test:lead_test@localhost:5432/lead_sla_test",
    "REDIS_URL": "redis://localhost:6379/0",
    "SECRET_KEY": "test-secret-key",
    "WEBHOOK_SHARED_SECRET": "test-webhook-secret",
    "LLM_API_KEY": "test-llm-key",
    "LLM_MODEL_FAST": "stable-fast-model",
    "LLM_MODEL_REPLY": "stable-reply-model",
    "EMBEDDING_API_KEY": "test-embedding-key",
    "EMBEDDING_MODEL": "stable-text-embedding",
    "TELEGRAM_BOT_TOKEN": "test-telegram-token",
    "WHATSAPP_PROVIDER_TOKEN": "test-whatsapp-token",
    "EMAIL_API_KEY": "test-email-key",
    "EMAIL_SENDER": "leads@example.test",
    "CALENDAR_API_TOKEN": "test-calendar-token",
    "CRM_API_TOKEN": "test-crm-token",
    "MAX_AUTONOMOUS_TURNS": "6",
    "MAX_TOOL_CALLS_PER_TURN": "3",
    "MAX_INDEX_AGE_HOURS": "24",
}


def load_workflow() -> dict:
    with WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        return yaml.safe_load(workflow_file)


def test_ci_workflow_has_required_steps() -> None:
    workflow = load_workflow()
    steps = workflow["jobs"]["test"]["steps"]
    step_names = {step.get("name") for step in steps}

    assert {"Lint", "Format check", "Run tests"} <= step_names


def test_ci_workflow_declares_required_services() -> None:
    workflow = load_workflow()
    services = workflow["jobs"]["test"]["services"]

    assert "postgres" in services
    assert "redis" in services

    for service_name in ("postgres", "redis"):
        service = services[service_name]
        assert "image" in service
        assert "--health-cmd" in service["options"]
        assert "--health-interval" in service["options"]
        assert "--health-timeout" in service["options"]
        assert "--health-retries" in service["options"]


def test_ci_workflow_sets_required_test_env() -> None:
    workflow = load_workflow()
    run_tests_step = next(
        step for step in workflow["jobs"]["test"]["steps"] if step.get("name") == "Run tests"
    )

    assert run_tests_step["env"] == EXPECTED_TEST_ENV
