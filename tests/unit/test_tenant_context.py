from __future__ import annotations

import uuid
from typing import Any

import pytest

from lead_sla_agent.db.repositories import LeadRepository


class FakeScalarResult:
    def all(self) -> list[Any]:
        return []


class FakeResult:
    def scalar_one_or_none(self) -> None:
        return None

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult()


class FakeSession:
    def __init__(self) -> None:
        self.executions: list[tuple[Any, dict[str, str] | None]] = []

    async def execute(
        self,
        statement: Any,
        parameters: dict[str, str] | None = None,
    ) -> FakeResult:
        self.executions.append((statement, parameters))
        return FakeResult()


@pytest.mark.asyncio
async def test_repository_requires_tenant_context() -> None:
    tenant_id = uuid.uuid4()
    lead_id = uuid.uuid4()
    session = FakeSession()
    repository = LeadRepository(session)  # type: ignore[arg-type]

    await repository.get_lead(tenant_id=tenant_id, lead_id=lead_id)

    assert len(session.executions) == 2
    tenant_context_statement, tenant_context_parameters = session.executions[0]
    assert str(tenant_context_statement) == "SELECT set_config('app.tenant_id', :tenant_id, true)"
    assert tenant_context_parameters == {"tenant_id": str(tenant_id)}

    with pytest.raises(ValueError, match="tenant_id is required"):
        await repository.get_lead(tenant_id=None, lead_id=lead_id)  # type: ignore[arg-type]
