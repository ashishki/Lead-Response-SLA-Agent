"""Append-only audit event repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import AuditEvent
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class AuditEventRepository:
    """Append-only audit event writer."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def append(
        self,
        tenant_id: uuid.UUID,
        event_type: str,
        actor_type: str,
        event_metadata: dict[str, Any],
    ) -> AuditEvent:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        with self.tracer.start_as_current_span("db.audit.append"):
            await apply_tenant_context(self.session, tenant_id)
            event = AuditEvent(
                tenant_id=tenant_id,
                event_type=event_type,
                actor_type=actor_type,
                event_metadata=event_metadata,
            )
            self.session.add(event)
            await self.session.flush()
            return event
