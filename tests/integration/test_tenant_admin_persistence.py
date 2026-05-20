from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lead_sla_agent.db.base import Base
from lead_sla_agent.db.models import Tenant, TenantConfig, TenantConfigAudit
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.db.tenant_config_repository import TenantConfigVersionConflict
from lead_sla_agent.operator.tenant_admin import PersistentTenantAdminStore

_TENANT_CONFIG_SPEC = spec_from_file_location(
    "tenant_config_migration",
    Path("alembic/versions/0005_tenant_config.py"),
)
assert _TENANT_CONFIG_SPEC is not None
assert _TENANT_CONFIG_SPEC.loader is not None
tenant_config_migration = module_from_spec(_TENANT_CONFIG_SPEC)
_TENANT_CONFIG_SPEC.loader.exec_module(tenant_config_migration)

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
        for statement in tenant_config_migration.UPGRADE_RLS_STATEMENTS:
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
async def test_tenant_config_survives_restart_and_loads_by_tenant_id(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        updated = await store.update_config(
            tenant_id=str(TENANT_A),
            actor_id="operator-1",
            actor_role="operator",
            changes={
                "channels": ["website_form", "sms"],
                "business_hours": {
                    "timezone": "America/Chicago",
                    "days": ["mon-sat"],
                    "hours": "07-19",
                },
                "required_fields": ["customer_name", "phone", "door_issue", "urgency"],
                "max_turns": 5,
                "provider_settings": {"outbound_channel": "sms"},
            },
        )
        await session.commit()

    assert updated.version == 2

    async with sessionmaker() as restarted_session:
        store = PersistentTenantAdminStore(session=restarted_session)
        persisted = await store.get_config(str(TENANT_A))
        other_tenant = await store.get_config(str(TENANT_B))

    assert persisted.version == 2
    assert persisted.config["channels"] == ["website_form", "sms"]
    assert persisted.config["max_turns"] == 5
    assert other_tenant.version == 1
    assert other_tenant.config["channels"] == ["website_form"]


@pytest.mark.asyncio
async def test_tenant_config_mutations_create_versions_and_immutable_audit_records(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        owner_update = await store.update_config(
            tenant_id=str(TENANT_A),
            actor_id="owner-1",
            actor_role="owner",
            changes={"handoff_policy": ["unsupported_question", "high_value_lead"]},
        )
        approved_update = await store.update_config(
            tenant_id=str(TENANT_A),
            actor_id="operator-1",
            actor_role="operator",
            changes={"unsafe_categories": ["pricing_commitment", "complaint_or_refund"]},
            approval_id="approval-1",
        )
        await session.commit()

    assert owner_update.version == 2
    assert approved_update.version == 3

    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        history = await store.history(str(TENANT_A))
        other_tenant_history = await store.history(str(TENANT_B))

    assert [event["event_metadata"]["new_version"] for event in history] == [2, 3]
    assert [event["event_metadata"]["dangerous_change"] for event in history] == [True, True]
    assert history[-1]["event_metadata"]["approval_id"] == "approval-1"
    assert other_tenant_history == []


@pytest.mark.asyncio
async def test_dangerous_policy_change_requires_owner_or_approval_for_persistent_store(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)

        with pytest.raises(
            PermissionError,
            match="dangerous tenant config changes require owner role or approval",
        ):
            await store.update_config(
                tenant_id=str(TENANT_A),
                actor_id="operator-1",
                actor_role="operator",
                changes={"autonomous_send_enabled": False},
            )

        with pytest.raises(ValueError, match="unsupported tenant config fields"):
            await store.update_config(
                tenant_id=str(TENANT_A),
                actor_id="operator-1",
                actor_role="operator",
                changes={"raw_prompt_override": "unsafe"},
            )


@pytest.mark.asyncio
async def test_tenant_config_uses_optimistic_version_conflict_detection(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        current = await store.get_config(str(TENANT_A))
        updated = await store.update_config(
            tenant_id=str(TENANT_A),
            actor_id="operator-1",
            actor_role="operator",
            changes={"max_turns": 5},
            expected_version=current.version,
        )

        with pytest.raises(TenantConfigVersionConflict, match="tenant config version conflict"):
            await store.update_config(
                tenant_id=str(TENANT_A),
                actor_id="operator-2",
                actor_role="operator",
                changes={"max_turns": 4},
                expected_version=current.version,
            )

    assert updated.version == 2


@pytest.mark.asyncio
async def test_tenant_config_repository_checks_and_rls_deny_cross_tenant_access(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        await store.update_config(
            tenant_id=str(TENANT_A),
            actor_id="operator-1",
            actor_role="operator",
            changes={"max_turns": 5},
        )
        await session.commit()

    async with sessionmaker() as session:
        store = PersistentTenantAdminStore(session=session)
        tenant_b_config = await store.get_config(str(TENANT_B))
        tenant_b_history = await store.history(str(TENANT_B))

    assert tenant_b_config.version == 1
    assert tenant_b_config.config["max_turns"] == 6
    assert tenant_b_history == []

    async with sessionmaker() as session:
        await session.execute(text("SET ROLE lead_rls_app"))
        await apply_tenant_context(session, TENANT_B)
        config_result = await session.execute(select(TenantConfig))
        audit_result = await session.execute(select(TenantConfigAudit))

    assert config_result.scalars().all() == []
    assert audit_result.scalars().all() == []


def test_tenant_config_migration_defines_rls_for_config_tables() -> None:
    migration_text = " ".join(
        str(statement) for statement in tenant_config_migration.UPGRADE_RLS_STATEMENTS
    )
    for table_name in tenant_config_migration.TENANT_CONFIG_TABLES:
        assert "ALTER TABLE " + table_name + " ENABLE ROW LEVEL SECURITY" in migration_text
        assert "ALTER TABLE " + table_name + " FORCE ROW LEVEL SECURITY" in migration_text
        assert "CREATE POLICY tenant_isolation ON " + table_name in migration_text
