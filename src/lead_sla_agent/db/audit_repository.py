"""PostgreSQL-backed canonical audit event repository."""

from __future__ import annotations

import uuid
from copy import deepcopy

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.audit.events import (
    AuditEventInput,
    AuditEventRecord,
    authorize_audit_search,
    isoformat,
    validate_audit_event,
)
from lead_sla_agent.db.models import AuditLogEvent
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class AuditLogRepository:
    """Append-only canonical tenant audit event store."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def append(self, event: AuditEventInput) -> AuditEventRecord:
        validate_audit_event(event)
        tenant_uuid = _require_uuid_tenant_id(event.tenant_id)

        with self.tracer.start_as_current_span("db.audit_log.append"):
            await apply_tenant_context(self.session, tenant_uuid)
            row = AuditLogEvent(
                tenant_id=tenant_uuid,
                actor_ref=event.actor_ref,
                action=event.action,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                result=event.result,
                policy_version=event.policy_version,
                payload=deepcopy(event.payload),
            )
            self.session.add(row)
            await self.session.flush()
            return _record(row)

    async def search(
        self,
        *,
        tenant_id: uuid.UUID | str,
        actor_role: str,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> list[AuditEventRecord]:
        authorize_audit_search(actor_role)
        tenant_uuid = _require_uuid_tenant_id(tenant_id)
        statement = select(AuditLogEvent).where(AuditLogEvent.tenant_id == tenant_uuid)
        if action is not None:
            statement = statement.where(AuditLogEvent.action == action)
        if resource_type is not None:
            statement = statement.where(AuditLogEvent.resource_type == resource_type)
        statement = statement.order_by(AuditLogEvent.created_at, AuditLogEvent.id)

        with self.tracer.start_as_current_span("db.audit_log.search"):
            await apply_tenant_context(self.session, tenant_uuid)
            result = await self.session.execute(statement)
            return [_record(row) for row in result.scalars().all()]


def _require_uuid_tenant_id(tenant_id: uuid.UUID | str | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    if isinstance(tenant_id, uuid.UUID):
        return tenant_id
    return uuid.UUID(tenant_id)


def _record(row: AuditLogEvent) -> AuditEventRecord:
    return AuditEventRecord(
        tenant_id=str(row.tenant_id),
        actor_ref=row.actor_ref,
        action=row.action,
        resource_type=row.resource_type,
        resource_id=row.resource_id,
        result=row.result,
        policy_version=row.policy_version,
        created_at=isoformat(row.created_at),
        payload=deepcopy(row.payload),
    )
