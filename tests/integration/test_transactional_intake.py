from __future__ import annotations

import json
import os
import uuid
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lead_sla_agent.api.app import create_app
from lead_sla_agent.db.base import Base
from lead_sla_agent.db.models import AuditEvent, Conversation, Lead, Message, ProviderEvent, Tenant
from lead_sla_agent.db.repositories import PersistentWebhookStore
from lead_sla_agent.intake.normalizer import normalize_inbound_event
from lead_sla_agent.intake.schemas import InboundWebhookPayload
from lead_sla_agent.intake.signatures import SIGNATURE_HEADER, build_signature
from lead_sla_agent.observability.metrics import metrics

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


@pytest.fixture()
async def sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://lead_test:lead_test@localhost:5432/lead_sla_test",
    )
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        await engine.dispose()
        pytest.skip("PostgreSQL service is not available: " + exc.__class__.__name__)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        session.add(Tenant(id=TENANT_ID, name="Tenant One", slug="tenant-one", status="active"))
        await session.commit()

    try:
        yield maker
    finally:
        await engine.dispose()


def _webhook_body(source_event_id: str = "evt-transactional") -> bytes:
    return json.dumps(
        {
            "tenant_id": str(TENANT_ID),
            "source_event_id": source_event_id,
            "channel": "website_form",
            "contact_name": "Private Lead",
            "contact_email": "private-lead@example.test",
            "contact_phone": "+15550101010",
            "message": "Need an appointment",
        },
        sort_keys=True,
    ).encode("utf-8")


async def _post_webhook(client: AsyncClient, raw_body: bytes) -> object:
    return await client.post(
        "/webhooks/inbound",
        content=raw_body,
        headers={
            "content-type": "application/json",
            SIGNATURE_HEADER: build_signature(raw_body, "test-webhook-secret"),
        },
    )


@pytest.mark.asyncio
async def test_persistent_webhook_replay_is_idempotent(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    metrics.reset()
    app = create_app()
    raw_body = _webhook_body()

    async with sessionmaker() as session:
        app.state.webhook_store = PersistentWebhookStore(session)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            first_response = await _post_webhook(client, raw_body)
            second_response = await _post_webhook(client, raw_body)

        counts = await _row_counts(session)
        provider_event = await _provider_event(session)

    first = first_response.json()
    second = second_response.json()
    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert first["replayed"] is False
    assert second["replayed"] is True
    assert second["provider_event_id"] == first["provider_event_id"]
    assert second["lead_id"] == first["lead_id"]
    assert second["conversation_id"] == first["conversation_id"]
    assert counts == {
        "provider_event": 1,
        "lead": 1,
        "conversation": 1,
        "message": 1,
        "audit_event": 1,
    }
    assert provider_event.source_event_id == "evt-transactional"
    assert provider_event.payload_hash
    assert metrics.histograms["intake_latency_ms"]


@pytest.mark.asyncio
async def test_transcript_failure_rolls_back_whole_intake(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    event = _normalized_event("evt-transcript-failure")

    async with sessionmaker() as session:
        store = PersistentWebhookStore(
            session,
            transcript_repository_type=FailingTranscriptRepository,
        )

        with pytest.raises(RuntimeError, match="transcript failure"):
            await store.accept_event(event)

        counts = await _row_counts(session)

    assert counts == {
        "provider_event": 0,
        "lead": 0,
        "conversation": 0,
        "message": 0,
        "audit_event": 0,
    }


@pytest.mark.asyncio
async def test_audit_failure_rolls_back_and_payload_is_hash_only(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    raw_body = _webhook_body("evt-hash-only")
    event = _normalized_event("evt-audit-failure")

    async with sessionmaker() as session:
        store = PersistentWebhookStore(session)
        accepted = await store.accept_event(
            normalize_inbound_event(InboundWebhookPayload.model_validate_json(raw_body), raw_body)
        )
        provider_event = await _provider_event(session)
        audit_event = await _audit_event(session)
        baseline_counts = await _row_counts(session)

    assert accepted.replayed is False
    assert provider_event.payload_hash
    assert bytes(provider_event.payload_hash, "utf-8") != raw_body
    assert audit_event.event_metadata["payload_hash"] == provider_event.payload_hash
    assert "Private Lead" not in str(audit_event.event_metadata)
    assert "private-lead@example.test" not in str(audit_event.event_metadata)

    async with sessionmaker() as session:
        store = PersistentWebhookStore(session, audit_repository_type=FailingAuditRepository)

        with pytest.raises(RuntimeError, match="audit failure"):
            await store.accept_event(event)

        counts = await _row_counts(session)

    assert (
        counts
        == baseline_counts
        == {
            "provider_event": 1,
            "lead": 1,
            "conversation": 1,
            "message": 1,
            "audit_event": 1,
        }
    )


class FailingTranscriptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append_message(self, **kwargs: object) -> object:
        raise RuntimeError("transcript failure")


class FailingAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append(self, **kwargs: object) -> object:
        raise RuntimeError("audit failure")


def _normalized_event(source_event_id: str) -> Any:
    return normalize_inbound_event(
        InboundWebhookPayload(
            tenant_id=TENANT_ID,
            source_event_id=source_event_id,
            channel="website_form",
            contact_name="Private Lead",
            contact_email="private-lead@example.test",
            contact_phone="+15550101010",
            message="Need an appointment",
        ),
        _webhook_body(source_event_id),
    )


async def _row_counts(session: AsyncSession) -> dict[str, int]:
    tables = {
        "provider_event": ProviderEvent,
        "lead": Lead,
        "conversation": Conversation,
        "message": Message,
        "audit_event": AuditEvent,
    }
    counts = {}
    for table_name, model in tables.items():
        result = await session.execute(select(func.count()).select_from(model))
        counts[table_name] = result.scalar_one()
    return counts


async def _provider_event(session: AsyncSession) -> ProviderEvent:
    result = await session.execute(select(ProviderEvent))
    return result.scalar_one()


async def _audit_event(session: AsyncSession) -> AuditEvent:
    result = await session.execute(select(AuditEvent))
    return result.scalar_one()
