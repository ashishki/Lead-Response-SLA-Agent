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

from lead_sla_agent.billing.usage import (
    PRICING_PACKAGE_MAPPING_VERSION,
    PersistentUsageMeter,
    UsageEvent,
)
from lead_sla_agent.db.base import Base
from lead_sla_agent.db.models import Tenant, UsageLedgerEvent
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.db.usage_repository import UsageRepository

_USAGE_LEDGER_SPEC = spec_from_file_location(
    "usage_ledger_migration",
    Path("alembic/versions/0006_usage_ledger.py"),
)
assert _USAGE_LEDGER_SPEC is not None
assert _USAGE_LEDGER_SPEC.loader is not None
usage_ledger_migration = module_from_spec(_USAGE_LEDGER_SPEC)
_USAGE_LEDGER_SPEC.loader.exec_module(usage_ledger_migration)

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
        for statement in usage_ledger_migration.UPGRADE_RLS_STATEMENTS:
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
async def test_usage_ledger_is_append_only_tenant_scoped_and_survives_restart(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        meter = PersistentUsageMeter(UsageRepository(session))
        recorded = await meter.record_event(
            _event("usage-1", TENANT_A, "lead_processed", metadata={"channel": "website_form"})
        )
        await session.commit()

    assert recorded.event_id == "usage-1"

    async with sessionmaker() as restarted_session:
        meter = PersistentUsageMeter(UsageRepository(restarted_session))
        tenant_a = await meter.monthly_export(str(TENANT_A), 2026, 5)
        tenant_b = await meter.monthly_export(str(TENANT_B), 2026, 5)

    assert tenant_a["usage"]["leads_processed"] == 1
    assert tenant_b["usage"]["leads_processed"] == 0


@pytest.mark.asyncio
async def test_duplicate_usage_event_ids_are_idempotent(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        meter = PersistentUsageMeter(UsageRepository(session))
        first = await meter.record_event(
            _event("usage-1", TENANT_A, "provider_send", metadata={"provider": "sms"})
        )
        duplicate = await meter.record_event(
            _event("usage-1", TENANT_A, "provider_send", metadata={"provider": "sms"})
        )
        await session.commit()

    assert duplicate == first

    async with sessionmaker() as session:
        rows = await UsageRepository(session).list_month_events(str(TENANT_A), 2026, 5)
        export = await PersistentUsageMeter(UsageRepository(session)).monthly_export(
            str(TENANT_A),
            2026,
            5,
        )

    assert len(rows) == 1
    assert export["usage"]["provider_sends"] == 1
    assert export["usage"]["provider_sends_by_provider"] == {"sms": 1}


@pytest.mark.asyncio
async def test_monthly_usage_export_is_deterministic_and_pricing_versioned(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        meter = PersistentUsageMeter(UsageRepository(session))
        for event in reversed(_usage_events()):
            await meter.record_event(event)
        await session.commit()

    expected_usage = {
        "leads_processed": 2,
        "ai_assisted_replies": 1,
        "provider_sends": 2,
        "review_tasks": 1,
        "bookings": 1,
        "active_channels": ["sms", "website_form"],
        "provider_sends_by_provider": {"email": 1, "sms": 1},
    }

    async with sessionmaker() as session:
        first_export = await PersistentUsageMeter(UsageRepository(session)).monthly_export(
            str(TENANT_A),
            2026,
            5,
        )

    async with sessionmaker() as restarted_session:
        second_export = await PersistentUsageMeter(
            UsageRepository(restarted_session)
        ).monthly_export(
            str(TENANT_A),
            2026,
            5,
        )

    assert first_export == second_export
    assert first_export["pricing_mapping_version"] == PRICING_PACKAGE_MAPPING_VERSION
    assert first_export["usage"] == expected_usage
    assert first_export["pricing_experiment_mapping"]["Recovery Pilot"] == {
        "primary_metric": "bookings",
        "bookings": 1,
        "review_tasks": 1,
    }
    serialized = str(first_export)
    assert "customer" not in serialized.lower()
    assert "phone" not in serialized.lower()
    assert "email@example" not in serialized


@pytest.mark.asyncio
async def test_persistent_usage_ledger_rejects_unsupported_metadata_and_pii_values(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        meter = PersistentUsageMeter(UsageRepository(session))

        with pytest.raises(ValueError, match="usage metadata contains unsupported or PII fields"):
            await meter.record_event(
                _event("usage-pii-key", TENANT_A, "lead_processed", metadata={"email": "x@y.test"})
            )

        with pytest.raises(ValueError, match="usage metadata contains unsupported or PII fields"):
            await meter.record_event(
                _event(
                    "usage-pii-value",
                    TENANT_A,
                    "lead_processed",
                    metadata={"source": "customer@example.test"},
                )
            )


@pytest.mark.asyncio
async def test_usage_ledger_rls_denies_cross_tenant_direct_reads(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        meter = PersistentUsageMeter(UsageRepository(session))
        await meter.record_event(
            _event("usage-1", TENANT_A, "lead_processed", metadata={"channel": "website_form"})
        )
        await session.commit()

    async with sessionmaker() as session:
        await session.execute(text("SET ROLE lead_rls_app"))
        await apply_tenant_context(session, TENANT_B)
        result = await session.execute(select(UsageLedgerEvent))

    assert result.scalars().all() == []


def test_usage_ledger_migration_defines_rls_for_ledger_table() -> None:
    migration_text = " ".join(
        str(statement) for statement in usage_ledger_migration.UPGRADE_RLS_STATEMENTS
    )
    for table_name in usage_ledger_migration.USAGE_LEDGER_TABLES:
        assert "ALTER TABLE " + table_name + " ENABLE ROW LEVEL SECURITY" in migration_text
        assert "ALTER TABLE " + table_name + " FORCE ROW LEVEL SECURITY" in migration_text
        assert "CREATE POLICY tenant_isolation ON " + table_name in migration_text


def _usage_events() -> list[UsageEvent]:
    return [
        _event("usage-lead-1", TENANT_A, "lead_processed", metadata={"channel": "website_form"}),
        _event("usage-lead-2", TENANT_A, "lead_processed", metadata={"channel": "sms"}),
        _event("usage-reply-1", TENANT_A, "ai_assisted_reply", metadata={"channel": "sms"}),
        _event("usage-send-1", TENANT_A, "provider_send", metadata={"provider": "sms"}),
        _event("usage-send-2", TENANT_A, "provider_send", metadata={"provider": "email"}),
        _event(
            "usage-review-1", TENANT_A, "review_task", metadata={"source": "unsupported_question"}
        ),
        _event("usage-booking-1", TENANT_A, "booking", metadata={"outcome": "booked"}),
        _event("usage-channel-1", TENANT_A, "active_channel", metadata={"channel": "website_form"}),
        _event("usage-channel-2", TENANT_A, "active_channel", metadata={"channel": "sms"}),
        _event(
            "usage-other-tenant", TENANT_B, "lead_processed", metadata={"channel": "website_form"}
        ),
        UsageEvent(
            tenant_id=str(TENANT_A),
            event_type="lead_processed",
            occurred_at=datetime(2026, 6, 1, tzinfo=UTC),
            metadata={"channel": "website_form"},
            event_id="usage-june-1",
        ),
    ]


def _event(
    event_id: str,
    tenant_id: uuid.UUID,
    event_type: str,
    metadata: dict[str, str],
) -> UsageEvent:
    return UsageEvent(
        tenant_id=str(tenant_id),
        event_type=event_type,
        occurred_at=datetime(2026, 5, 20, tzinfo=UTC),
        metadata=metadata,
        event_id=event_id,
    )
