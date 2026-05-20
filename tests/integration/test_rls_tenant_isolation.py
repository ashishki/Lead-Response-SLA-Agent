from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from datetime import date
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lead_sla_agent.db.base import Base
from lead_sla_agent.db.models import (
    AuditEvent,
    Conversation,
    HumanReviewApproval,
    HumanReviewTask,
    Lead,
    Message,
    OutcomeLabel,
    ProviderEvent,
    Tenant,
)
from lead_sla_agent.db.repositories import PersistentWebhookStore
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.intake.normalizer import normalize_inbound_event
from lead_sla_agent.intake.schemas import InboundWebhookPayload
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

_RLS_SPEC = spec_from_file_location(
    "rls_migration",
    Path("alembic/versions/0004_rls_policies.py"),
)
assert _RLS_SPEC is not None
assert _RLS_SPEC.loader is not None
rls_migration = module_from_spec(_RLS_SPEC)
_RLS_SPEC.loader.exec_module(rls_migration)

TENANT_A = uuid.UUID("00000000-0000-4000-8000-0000000000a1")
TENANT_B = uuid.UUID("00000000-0000-4000-8000-0000000000b2")
TENANT_SCOPED_MODELS = (
    Lead,
    Conversation,
    Message,
    AuditEvent,
    ProviderEvent,
    HumanReviewTask,
    HumanReviewApproval,
    OutcomeLabel,
)


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
        for statement in rls_migration.UPGRADE_STATEMENTS:
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
async def test_rls_policies_enabled_for_every_tenant_scoped_table(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        rows = await session.execute(
            text(
                "SELECT relname, relrowsecurity, relforcerowsecurity "
                "FROM pg_class WHERE relkind = 'r'"
            )
        )

    policy_state = {row.relname: row for row in rows if row.relname in rls_migration.TENANT_TABLES}
    assert set(policy_state) == set(rls_migration.TENANT_TABLES)
    assert all(row.relrowsecurity for row in policy_state.values())
    assert all(row.relforcerowsecurity for row in policy_state.values())


@pytest.mark.asyncio
async def test_rls_blocks_direct_cross_tenant_queries(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        await _seed_tenant_rows(session)
        await session.execute(text("SET ROLE lead_rls_app"))
        await apply_tenant_context(session, TENANT_B)

        visible_counts = {}
        for model in TENANT_SCOPED_MODELS:
            result = await session.execute(select(model))
            visible_counts[model.__tablename__] = len(result.scalars().all())

    assert visible_counts == {
        "lead": 0,
        "conversation": 0,
        "message": 0,
        "audit_event": 0,
        "provider_event": 0,
        "human_review_task": 0,
        "human_review_approval": 0,
        "outcome_label": 0,
    }


@pytest.mark.asyncio
async def test_rls_missing_tenant_context_fails_closed(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        await _seed_tenant_rows(session)

    async with sessionmaker() as session_without_context:
        await session_without_context.execute(text("SET ROLE lead_rls_app"))
        visible_counts = {}
        for model in TENANT_SCOPED_MODELS:
            result = await session_without_context.execute(select(model))
            visible_counts[model.__tablename__] = len(result.scalars().all())

    assert all(count == 0 for count in visible_counts.values())


def test_rls_migration_covers_every_tenant_scoped_table() -> None:
    migration_text = " ".join(str(statement) for statement in rls_migration.UPGRADE_STATEMENTS)
    for table_name in rls_migration.TENANT_TABLES:
        assert "ALTER TABLE " + table_name + " ENABLE ROW LEVEL SECURITY" in migration_text
        assert "ALTER TABLE " + table_name + " FORCE ROW LEVEL SECURITY" in migration_text
        assert "CREATE POLICY tenant_isolation ON " + table_name in migration_text


async def _seed_tenant_rows(session: AsyncSession) -> None:
    raw_body = b'{"source_event_id":"evt-rls"}'
    event = normalize_inbound_event(
        InboundWebhookPayload(
            tenant_id=TENANT_A,
            source_event_id="evt-rls",
            channel="website_form",
            contact_name="Private Lead",
            contact_email="private-lead@example.test",
            contact_phone="+15550101010",
            message="Need an appointment",
        ),
        raw_body,
    )
    accepted = await PersistentWebhookStore(session).accept_event(event)
    review_store = HumanReviewTaskStore(session=session)
    review = await review_store.create_human_review_task(
        tenant_id=TENANT_A,
        conversation_id=accepted.conversation_id,
        handoff_reason="unsupported_question",
        payload={"lead_id": str(accepted.lead_id)},
    )
    await review_store.approve_reply(
        tenant_id=TENANT_A,
        task_id=review["task_id"],
        actor_id="operator-1",
        original_draft="Original private draft",
        final_message="Approved private reply",
        reason_code="operator_edit",
    )
    await OutcomeStore(session=session).add_label(
        tenant_id=TENANT_A,
        lead_id=accepted.lead_id,
        label="booked",
        labeled_on=date(2026, 5, 20),
    )
    await session.commit()
