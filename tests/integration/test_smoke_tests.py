from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from scripts import smoke_test


@pytest.mark.asyncio
async def test_smoke_command_checks_core_deploy_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_migration_version(database_url: str | None) -> str:
        assert database_url == "postgresql+asyncpg://smoke-db"
        return "0007_audit_events"

    async def fake_redis(redis_url: str | None) -> str:
        assert redis_url == "redis://smoke-redis/0"
        return "ok"

    monkeypatch.setattr(smoke_test, "check_migration_version", fake_migration_version)
    monkeypatch.setattr(smoke_test, "check_redis", fake_redis)

    app = create_app()
    transport = ASGITransport(app=app)
    config = smoke_test.SmokeConfig(
        environment="staging",
        base_url="http://testserver",
        tenant_id="smoke-tenant",
        sandbox_mode=False,
        database_url="postgresql+asyncpg://smoke-db",
        redis_url="redis://smoke-redis/0",
    )

    async with AsyncClient(transport=transport, base_url=config.base_url) as client:
        result = await smoke_test.run_smoke_checks(config, client=client)

    assert result == {
        "environment": "staging",
        "status": "ok",
        "checks": {
            "health": "ok",
            "migration_version": "0007_audit_events",
            "redis": "ok",
            "operator_auth": "ok",
            "provider_sandbox": "skipped",
            "safe_handoff": "ok",
        },
    }


@pytest.mark.asyncio
async def test_provider_sandbox_is_skipped_unless_explicitly_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingAdapter:
        async def send_message(self, **kwargs: Any) -> Any:
            raise AssertionError("provider sandbox send should be skipped")

    monkeypatch.setattr(smoke_test, "FakeMessagingAdapter", FailingAdapter)

    assert await smoke_test.check_provider_sandbox(sandbox_mode=False) == "skipped"


@pytest.mark.asyncio
async def test_provider_sandbox_mode_uses_fake_sandbox_recipient_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, str | None]] = []

    class RecordingAdapter:
        async def send_message(
            self,
            *,
            channel: str,
            recipient: str,
            text: str,
            idempotency_key: str | None = None,
        ) -> Any:
            calls.append(
                {
                    "channel": channel,
                    "recipient": recipient,
                    "text": text,
                    "idempotency_key": idempotency_key,
                }
            )
            return SimpleNamespace(status="sent")

    monkeypatch.setattr(smoke_test, "FakeMessagingAdapter", RecordingAdapter)

    assert await smoke_test.check_provider_sandbox(sandbox_mode=True) == "ok"
    assert calls == [
        {
            "channel": "email",
            "recipient": "sandbox@example.test",
            "text": "sandbox smoke test",
            "idempotency_key": "smoke:sandbox:message",
        }
    ]


@pytest.mark.asyncio
async def test_safe_handoff_queues_unsafe_message_without_provider_send() -> None:
    assert await smoke_test.check_safe_handoff() == "ok"


@pytest.mark.asyncio
async def test_smoke_checks_require_database_and_redis_urls() -> None:
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        await smoke_test.check_migration_version(None)

    with pytest.raises(RuntimeError, match="REDIS_URL is required"):
        await smoke_test.check_redis(None)


@pytest.mark.asyncio
async def test_operator_auth_check_hits_authenticated_route() -> None:
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert await smoke_test.check_operator_auth(client, "smoke-tenant") == "ok"


def test_smoke_cli_supports_staging_and_production_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://db")
    monkeypatch.setenv("REDIS_URL", "redis://redis/0")
    monkeypatch.setattr(
        "sys.argv",
        [
            "smoke_test.py",
            "--environment",
            "production",
            "--base-url",
            "https://app.example.test",
            "--tenant-id",
            "smoke-production",
            "--sandbox-mode",
        ],
    )

    config = smoke_test.parse_args()

    assert config == smoke_test.SmokeConfig(
        environment="production",
        base_url="https://app.example.test",
        tenant_id="smoke-production",
        sandbox_mode=True,
        database_url="postgresql+asyncpg://db",
        redis_url="redis://redis/0",
    )


def test_deploy_workflow_requires_staging_smoke_before_production_promotion() -> None:
    workflow_text = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)

    assert workflow["jobs"]["production_deploy"]["needs"] == "staging_deploy"
    assert "scripts/smoke_test.py --environment staging" in workflow_text
    assert "scripts/smoke_test.py --environment production" in workflow_text
    assert "--sandbox-mode" in workflow_text
    assert workflow_text.index("--environment staging") < workflow_text.index(
        "--environment production"
    )


def test_runbook_documents_smoke_scope_and_no_real_customer_sends() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "python scripts/smoke_test.py --environment staging" in content
    assert "python scripts/smoke_test.py --environment production" in content
    assert "API health, Alembic migration version, Redis connectivity" in content
    assert "operator auth, provider sandbox path, and unsafe-message handoff" in content
    assert "must never send to real customer recipients" in content
