"""Repository helpers that enforce tenant context for tenant-scoped reads."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import Conversation, Lead, ProviderEvent
from lead_sla_agent.db.tenant import apply_tenant_context


class TenantScopedRepository:
    """Base repository for tenant-scoped queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _execute_tenant_scoped(self, tenant_id: uuid.UUID, statement: Select[Any]) -> Any:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        await apply_tenant_context(self.session, tenant_id)
        return await self.session.execute(statement)


class LeadRepository(TenantScopedRepository):
    """Read helpers for lead and conversation state."""

    async def get_lead(self, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
        statement = select(Lead).where(Lead.tenant_id == tenant_id, Lead.id == lead_id)
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return result.scalar_one_or_none()

    async def list_conversations_for_lead(
        self,
        tenant_id: uuid.UUID,
        lead_id: uuid.UUID,
    ) -> list[Conversation]:
        statement = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.lead_id == lead_id,
        )
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return list(result.scalars().all())


class ProviderEventRepository(TenantScopedRepository):
    """Read helpers for provider event idempotency checks."""

    async def get_by_source_event_id(
        self,
        tenant_id: uuid.UUID,
        source_event_id: str,
    ) -> ProviderEvent | None:
        statement = select(ProviderEvent).where(
            ProviderEvent.tenant_id == tenant_id,
            ProviderEvent.source_event_id == source_event_id,
        )
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return result.scalar_one_or_none()
