from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lead_sla_agent.db.base import Base
from lead_sla_agent.db.lead_repository import LeadRepository, RepositoryPersistenceError
from lead_sla_agent.db.models import Tenant
from lead_sla_agent.db.transcript_repository import TranscriptRepository
from lead_sla_agent.intake.schemas import NormalizedInboundEvent
from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

TENANT_A = uuid.UUID("00000000-0000-4000-8000-0000000000a1")
TENANT_B = uuid.UUID("00000000-0000-4000-8000-0000000000b2")
PRIVATE_EMAIL = "private-lead@example.test"


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
        session.add_all(
            [
                Tenant(id=TENANT_A, name="Tenant A", slug="tenant-a", status="active"),
                Tenant(id=TENANT_B, name="Tenant B", slug="tenant-b", status="active"),
            ]
        )
        await session.commit()

    try:
        yield maker
    finally:
        await engine.dispose()


def normalized_event(tenant_id: uuid.UUID = TENANT_A) -> NormalizedInboundEvent:
    return NormalizedInboundEvent(
        tenant_id=tenant_id,
        source_event_id="source-1",
        channel="website_form",
        payload_hash="abc123",
        received_at=datetime.now(tz=UTC),
        contact_name="Private Lead",
        contact_email=PRIVATE_EMAIL,
        contact_phone="+15550101010",
        message="Need a private appointment tomorrow",
    )


@pytest.mark.asyncio
async def test_persistent_repositories_survive_restart_and_enforce_tenant_scope(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        lead_repository = LeadRepository(session)
        transcript_repository = TranscriptRepository(session)
        review_store = HumanReviewTaskStore(session=session)
        outcome_store = OutcomeStore(session=session)

        created = await lead_repository.create_from_event(normalized_event())
        inbound = await transcript_repository.append_message(
            tenant_id=TENANT_A,
            conversation_id=created.conversation.id,
            role="inbound",
            channel="website_form",
            content="Need a private appointment tomorrow",
            provider_message_id="provider-message-private",
        )
        review = await review_store.create_human_review_task(
            tenant_id=TENANT_A,
            conversation_id=created.conversation.id,
            handoff_reason="unsupported_question",
            payload={"lead_id": str(created.lead.id), "transcript_refs": [str(inbound.id)]},
        )
        approval = await review_store.approve_reply(
            tenant_id=TENANT_A,
            task_id=review["task_id"],
            actor_id="operator-1",
            original_draft="Original private draft",
            final_message="Approved private reply",
            reason_code="operator_edit",
        )
        outcome = await outcome_store.add_label(
            tenant_id=TENANT_A,
            lead_id=created.lead.id,
            label="booked",
            labeled_on=date(2026, 5, 20),
        )
        tenant_context = await session.execute(
            text("SELECT current_setting(:name, true)"), {"name": "app.tenant_id"}
        )
        await session.commit()

    assert tenant_context.scalar_one() == str(TENANT_A)
    assert approval["original_draft_hash"]
    assert approval["final_message_hash"]
    assert outcome["label"] == "booked"

    async with sessionmaker() as restarted_session:
        lead_repository = LeadRepository(restarted_session)
        transcript_repository = TranscriptRepository(restarted_session)
        review_store = HumanReviewTaskStore(session=restarted_session)
        outcome_store = OutcomeStore(session=restarted_session)

        persisted_lead = await lead_repository.get_lead(TENANT_A, created.lead.id)
        wrong_tenant_lead = await lead_repository.get_lead(TENANT_B, created.lead.id)
        persisted_conversation = await lead_repository.get_conversation(
            TENANT_A,
            created.conversation.id,
        )
        messages = await transcript_repository.list_messages(TENANT_A, created.conversation.id)
        wrong_tenant_messages = await transcript_repository.list_messages(
            TENANT_B,
            created.conversation.id,
        )
        reviews = await review_store.list_tasks(TENANT_A)
        wrong_tenant_reviews = await review_store.list_tasks(TENANT_B)
        persisted_approval = await review_store.get_approval(TENANT_A, review["task_id"])
        labels = await outcome_store.query_labels(
            TENANT_A,
            date(2026, 5, 1),
            date(2026, 5, 31),
        )
        wrong_tenant_labels = await outcome_store.query_labels(
            TENANT_B,
            date(2026, 5, 1),
            date(2026, 5, 31),
        )

    assert persisted_lead is not None
    assert persisted_lead.contact_email == PRIVATE_EMAIL
    assert persisted_conversation is not None
    assert wrong_tenant_lead is None
    assert len(messages) == 1
    assert messages[0].redacted_preview == REDACTED_VALUE
    assert messages[0].content_hash
    assert wrong_tenant_messages == []
    assert reviews == [
        {
            "task_id": review["task_id"],
            "tenant_id": str(TENANT_A),
            "conversation_id": str(created.conversation.id),
            "handoff_reason": "unsupported_question",
            "payload": {"lead_id": str(created.lead.id), "transcript_refs": [str(inbound.id)]},
            "status": "sent",
        }
    ]
    assert wrong_tenant_reviews == []
    assert persisted_approval is not None
    assert persisted_approval["task_id"] == review["task_id"]
    assert labels == [
        {
            "tenant_id": str(TENANT_A),
            "lead_id": str(created.lead.id),
            "label": "booked",
            "labeled_on": "2026-05-20",
        }
    ]
    assert wrong_tenant_labels == []


@pytest.mark.asyncio
async def test_persistent_repositories_require_tenant_id(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    conversation_id = uuid.uuid4()
    lead_id = uuid.uuid4()
    async with sessionmaker() as session:
        lead_repository = LeadRepository(session)
        transcript_repository = TranscriptRepository(session)
        review_store = HumanReviewTaskStore(session=session)
        outcome_store = OutcomeStore(session=session)

        with pytest.raises(ValueError, match="tenant_id is required"):
            await lead_repository.get_lead(None, lead_id)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="tenant_id is required"):
            await transcript_repository.list_messages(None, conversation_id)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="tenant_id is required"):
            await review_store.list_tasks(None)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="tenant_id is required"):
            await outcome_store.query_labels(None, date(2026, 5, 1), date(2026, 5, 31))  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_persistent_repository_exceptions_do_not_include_pii(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    missing_tenant = uuid.UUID("00000000-0000-4000-8000-000000000099")
    async with sessionmaker() as session:
        repository = LeadRepository(session)

        with pytest.raises(RepositoryPersistenceError) as exc_info:
            await repository.create_from_event(normalized_event(missing_tenant))

    message = str(exc_info.value)
    assert "repository persistence failed" in message
    assert PRIVATE_EMAIL not in message
    assert "Private Lead" not in message
    assert "+15550101010" not in message
