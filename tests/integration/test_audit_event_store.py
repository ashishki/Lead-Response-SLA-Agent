from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lead_sla_agent.audit.events import AUDIT_EVENT_POLICY_VERSION, AuditEventInput
from lead_sla_agent.billing.usage import PersistentUsageMeter, UsageEvent
from lead_sla_agent.db.audit_repository import AuditLogRepository
from lead_sla_agent.db.base import Base
from lead_sla_agent.db.models import AuditLogEvent, Conversation, Lead, Tenant
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.db.usage_repository import UsageRepository
from lead_sla_agent.operator.data_admin import TenantDataAdmin
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore
from lead_sla_agent.operator.tenant_admin import PersistentTenantAdminStore

_AUDIT_EVENT_SPEC = spec_from_file_location(
    "audit_event_migration",
    Path("alembic/versions/0007_audit_events.py"),
)
assert _AUDIT_EVENT_SPEC is not None
assert _AUDIT_EVENT_SPEC.loader is not None
audit_event_migration = module_from_spec(_AUDIT_EVENT_SPEC)
_AUDIT_EVENT_SPEC.loader.exec_module(audit_event_migration)

TENANT_A = uuid.UUID("00000000-0000-4000-8000-0000000000a1")
TENANT_B = uuid.UUID("00000000-0000-4000-8000-0000000000b2")


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
        for statement in audit_event_migration.UPGRADE_RLS_STATEMENTS:
            await connection.execute(statement)
        await connection.execute(
            text(
                "DO $$ BEGIN "
                "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'lead_rls_app') "
                "THEN CREATE ROLE lead_rls_app; END IF; "
                "END $$"
            )
        )
        await connection.execute(text("GRANT USAGE ON SCHEMA public TO lead_rls_app"))
        await connection.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES "
                "IN SCHEMA public TO lead_rls_app"
            )
        )

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


@pytest.mark.asyncio
async def test_audit_events_are_append_only_and_include_required_fields(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        repository = AuditLogRepository(session)
        created = await repository.append(
            AuditEventInput(
                tenant_id=str(TENANT_A),
                actor_ref="operator:operator-1",
                action="provider_send.completed",
                resource_type="message_send",
                resource_id="send-1",
                result="success",
                payload={"idempotency_key_hash": "sha256:abc123"},
            )
        )
        await session.commit()

    assert created.tenant_id == str(TENANT_A)
    assert created.actor_ref == "operator:operator-1"
    assert created.action == "provider_send.completed"
    assert created.resource_type == "message_send"
    assert created.resource_id == "send-1"
    assert created.result == "success"
    assert created.policy_version == AUDIT_EVENT_POLICY_VERSION
    assert created.created_at

    async with sessionmaker() as session:
        rows = await AuditLogRepository(session).search(tenant_id=TENANT_A, actor_role="owner")

    assert len(rows) == 1
    assert rows[0] == created


@pytest.mark.asyncio
async def test_audit_event_payload_rejects_pii_and_secrets(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        repository = AuditLogRepository(session)
        with pytest.raises(ValueError, match="audit payload contains PII or secrets"):
            await repository.append(
                AuditEventInput(
                    tenant_id=str(TENANT_A),
                    actor_ref="operator:operator-1",
                    action="bad.audit",
                    resource_type="lead",
                    resource_id="lead-1",
                    result="blocked",
                    payload={"email": "customer@example.test"},
                )
            )
        with pytest.raises(ValueError, match="audit payload contains PII or secrets"):
            await repository.append(
                AuditEventInput(
                    tenant_id=str(TENANT_A),
                    actor_ref="operator:operator-1",
                    action="bad.audit",
                    resource_type="secret",
                    resource_id="secret-1",
                    result="blocked",
                    payload={"authorization": "Bearer test-token"},
                )
            )


@pytest.mark.asyncio
async def test_audit_search_is_role_gated_tenant_scoped_and_rls_protected(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        repository = AuditLogRepository(session)
        await repository.append(
            AuditEventInput(
                tenant_id=str(TENANT_A),
                actor_ref="system:intake",
                action="webhook.accepted",
                resource_type="provider_event",
                resource_id="provider-event-1",
                result="success",
                payload={"payload_hash": "abc123"},
            )
        )
        await session.commit()

    async with sessionmaker() as session:
        repository = AuditLogRepository(session)
        visible = await repository.search(tenant_id=TENANT_A, actor_role="operator")
        hidden = await repository.search(tenant_id=TENANT_B, actor_role="operator")
        with pytest.raises(PermissionError, match="audit search requires owner or operator role"):
            await repository.search(tenant_id=TENANT_A, actor_role="viewer")

    assert [event.action for event in visible] == ["webhook.accepted"]
    assert hidden == []

    async with sessionmaker() as session:
        await session.execute(text("SET ROLE lead_rls_app"))
        await apply_tenant_context(session, TENANT_B)
        result = await session.execute(select(AuditLogEvent))

    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_existing_persistent_flows_emit_canonical_audit_events(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        conversation_id = await _seed_conversation(session)
        await PersistentTenantAdminStore(session=session).update_config(
            tenant_id=str(TENANT_A),
            actor_id="operator-1",
            actor_role="operator",
            changes={"max_turns": 5},
        )
        await PersistentUsageMeter(UsageRepository(session)).record_event(
            UsageEvent(
                tenant_id=str(TENANT_A),
                event_type="lead_processed",
                occurred_at=datetime(2026, 5, 20, tzinfo=UTC),
                metadata={"channel": "website_form"},
                event_id="usage-1",
            )
        )
        review_store = HumanReviewTaskStore(session=session)
        review = await review_store.create_human_review_task(
            tenant_id=TENANT_A,
            conversation_id=conversation_id,
            handoff_reason="unsupported_question",
            payload={"lead_id": "lead-ref-1"},
        )
        await review_store.approve_reply(
            tenant_id=TENANT_A,
            task_id=review["task_id"],
            actor_id="operator-1",
            original_draft="Original safe draft",
            final_message="Approved safe reply",
            reason_code="operator_edit",
        )
        await session.commit()

    async with sessionmaker() as session:
        events = await AuditLogRepository(session).search(tenant_id=TENANT_A, actor_role="owner")

    assert {event.action for event in events} == {
        "tenant_config.updated",
        "usage_event.recorded",
        "human_review_task.created",
        "human_review_reply.approved",
    }
    assert all(event.policy_version == AUDIT_EVENT_POLICY_VERSION for event in events)
    assert "Original safe draft" not in str(events)
    assert "Approved safe reply" not in str(events)


def test_data_admin_flow_emits_canonical_audit_fields() -> None:
    audit_record = TenantDataAdmin(leads=[{"tenant_id": "tenant-1"}]).anonymize_tenant_data(
        tenant_id="tenant-1",
        actor_id="operator-1",
        reason="customer_delete_request",
    )

    assert audit_record["actor_ref"] == "operator:operator-1"
    assert audit_record["action"] == "tenant_data.anonymized"
    assert audit_record["resource_type"] == "tenant"
    assert audit_record["resource_id"] == "tenant-1"
    assert audit_record["result"] == "success"
    assert audit_record["policy_version"] == AUDIT_EVENT_POLICY_VERSION


def test_audit_event_migration_defines_rls_for_event_table() -> None:
    migration_text = " ".join(
        str(statement) for statement in audit_event_migration.UPGRADE_RLS_STATEMENTS
    )
    for table_name in audit_event_migration.AUDIT_EVENT_TABLES:
        assert "ALTER TABLE " + table_name + " ENABLE ROW LEVEL SECURITY" in migration_text
        assert "ALTER TABLE " + table_name + " FORCE ROW LEVEL SECURITY" in migration_text
        assert "CREATE POLICY tenant_isolation ON " + table_name in migration_text


async def _seed_conversation(session: AsyncSession) -> uuid.UUID:
    lead = Lead(tenant_id=TENANT_A, source_channel="website_form", status="new")
    session.add(lead)
    await session.flush()
    conversation = Conversation(tenant_id=TENANT_A, lead_id=lead.id, status="open")
    session.add(conversation)
    await session.flush()
    return conversation.id
