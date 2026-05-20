from __future__ import annotations

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID

from lead_sla_agent.db import models as _models  # noqa: F401
from lead_sla_agent.db.base import Base

EXPECTED_TABLES = {
    "tenant",
    "lead",
    "conversation",
    "message",
    "audit_event",
    "provider_event",
    "human_review_task",
    "human_review_approval",
    "outcome_label",
    "tenant_config",
    "tenant_config_audit",
    "usage_ledger_event",
    "audit_log_event",
}


def test_initial_tables_declared() -> None:
    assert set(Base.metadata.tables) >= EXPECTED_TABLES

    for table_name in EXPECTED_TABLES:
        table = Base.metadata.tables[table_name]
        assert table.c.id.primary_key
        assert isinstance(table.c.id.type, UUID)
        assert table.c.id.type.as_uuid
        assert "created_at" in table.c
        assert isinstance(table.c.created_at.type, DateTime)
        assert table.c.created_at.type.timezone
