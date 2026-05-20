from __future__ import annotations

import inspect
import uuid
from typing import Any

import pytest

from lead_sla_agent.db.audit import AuditEventRepository
from lead_sla_agent.db.models import AuditEvent


class FakeSession:
    def __init__(self) -> None:
        self.executions: list[tuple[Any, dict[str, str] | None]] = []
        self.added: list[Any] = []
        self.flush_count = 0

    async def execute(
        self,
        statement: Any,
        parameters: dict[str, str] | None = None,
    ) -> None:
        self.executions.append((statement, parameters))

    def add(self, value: Any) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        self.flush_count += 1


@pytest.mark.asyncio
async def test_audit_repository_append_only_interface() -> None:
    tenant_id = uuid.uuid4()
    session = FakeSession()
    repository = AuditEventRepository(session)  # type: ignore[arg-type]

    event = await repository.append(
        tenant_id=tenant_id,
        event_type="lead.created",
        actor_type="system",
        event_metadata={"source": "unit-test"},
    )

    assert isinstance(event, AuditEvent)
    assert event in session.added
    assert session.flush_count == 1
    assert str(session.executions[0][0]) == "SELECT set_config('app.tenant_id', :tenant_id, true)"
    assert session.executions[0][1] == {"tenant_id": str(tenant_id)}

    public_methods = {
        name
        for name, value in inspect.getmembers(AuditEventRepository, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    assert public_methods == {"append"}
