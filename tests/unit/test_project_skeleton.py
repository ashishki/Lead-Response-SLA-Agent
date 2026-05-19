from __future__ import annotations

import importlib

import pytest

from lead_sla_agent.config import Settings


def test_package_entrypoint_imports(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, bool]] = []

    def fake_run(app_import_path: str, *, factory: bool) -> None:
        calls.append((app_import_path, factory))

    uvicorn = pytest.importorskip("uvicorn")
    monkeypatch.setattr(uvicorn, "run", fake_run)

    entrypoint = importlib.import_module("lead_sla_agent.__main__")
    app_module, app_name = entrypoint.APP_IMPORT_PATH.split(":")

    assert getattr(importlib.import_module(app_module), app_name) is not None

    entrypoint.main()

    assert calls == [("lead_sla_agent.api.app:app", False)]


def test_settings_load_required_values(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {
        "APP_ENV": "local-test",
        "DATABASE_URL": "postgresql+asyncpg://lead_test:lead_test@localhost:5432/lead_sla_test",
        "REDIS_URL": "redis://localhost:6379/1",
        "SECRET_KEY": "test-secret-key",
        "WEBHOOK_SHARED_SECRET": "test-webhook-secret",
    }
    for key, value in expected.items():
        monkeypatch.setenv(key, value)

    settings = Settings()

    assert settings.app_env == expected["APP_ENV"]
    assert settings.database_url == expected["DATABASE_URL"]
    assert settings.redis_url == expected["REDIS_URL"]
    assert settings.secret_key == expected["SECRET_KEY"]
    assert settings.webhook_shared_secret == expected["WEBHOOK_SHARED_SECRET"]


def test_expected_modules_exist() -> None:
    expected_modules = [
        "lead_sla_agent.api",
        "lead_sla_agent.conversation",
        "lead_sla_agent.db",
        "lead_sla_agent.intake",
        "lead_sla_agent.observability",
        "lead_sla_agent.operator",
        "lead_sla_agent.retrieval",
        "lead_sla_agent.tools",
        "lead_sla_agent.workers",
    ]

    for module_name in expected_modules:
        assert importlib.import_module(module_name)
