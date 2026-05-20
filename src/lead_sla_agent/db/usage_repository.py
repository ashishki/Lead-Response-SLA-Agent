"""PostgreSQL-backed usage ledger repository."""

from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.audit.events import AuditEventInput
from lead_sla_agent.billing.usage import (
    PRICING_PACKAGE_MAPPING_VERSION,
    UsageEvent,
    validate_usage_event,
)
from lead_sla_agent.db.audit_repository import AuditLogRepository
from lead_sla_agent.db.models import UsageLedgerEvent
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class UsageLedgerPersistenceError(RuntimeError):
    """PII-safe usage ledger persistence failure."""


class UsageRepository:
    """Append-only tenant-scoped usage ledger."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def append_event(self, event: UsageEvent) -> UsageEvent:
        validate_usage_event(event)
        if not event.event_id:
            raise ValueError("usage event_id is required for persistent ledger")

        tenant_uuid = _require_uuid_tenant_id(event.tenant_id)
        with self.tracer.start_as_current_span("db.usage.append_event"):
            await apply_tenant_context(self.session, tenant_uuid)
            existing = await self._get_existing_event(tenant_uuid, event.event_id)
            if existing is not None:
                return _event(existing)

            row = UsageLedgerEvent(
                tenant_id=tenant_uuid,
                event_id=event.event_id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                quantity=event.quantity,
                metadata_=deepcopy(event.metadata),
                pricing_mapping_version=PRICING_PACKAGE_MAPPING_VERSION,
            )
            self.session.add(row)
            try:
                await self.session.flush()
            except SQLAlchemyError:
                raise UsageLedgerPersistenceError("usage ledger persistence failed") from None
            await AuditLogRepository(self.session).append(
                AuditEventInput(
                    tenant_id=str(tenant_uuid),
                    actor_ref="system:billing",
                    action="usage_event.recorded",
                    resource_type="usage_event",
                    resource_id=event.event_id,
                    result="success",
                    payload={
                        "event_type": event.event_type,
                        "quantity": event.quantity,
                        "pricing_mapping_version": PRICING_PACKAGE_MAPPING_VERSION,
                    },
                )
            )
            return _event(row)

    async def list_month_events(
        self,
        tenant_id: uuid.UUID | str,
        year: int,
        month: int,
    ) -> list[UsageEvent]:
        tenant_uuid = _require_uuid_tenant_id(tenant_id)
        start = datetime(year, month, 1, tzinfo=UTC)
        end = datetime(year + int(month == 12), 1 if month == 12 else month + 1, 1, tzinfo=UTC)
        statement = (
            select(UsageLedgerEvent)
            .where(
                UsageLedgerEvent.tenant_id == tenant_uuid,
                UsageLedgerEvent.occurred_at >= start,
                UsageLedgerEvent.occurred_at < end,
            )
            .order_by(UsageLedgerEvent.occurred_at, UsageLedgerEvent.event_id)
        )

        with self.tracer.start_as_current_span("db.usage.list_month"):
            await apply_tenant_context(self.session, tenant_uuid)
            result = await self.session.execute(statement)
            return [_event(row) for row in result.scalars().all()]

    async def _get_existing_event(
        self,
        tenant_id: uuid.UUID,
        event_id: str,
    ) -> UsageLedgerEvent | None:
        statement = select(UsageLedgerEvent).where(
            UsageLedgerEvent.tenant_id == tenant_id,
            UsageLedgerEvent.event_id == event_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


def _require_uuid_tenant_id(tenant_id: uuid.UUID | str | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    if isinstance(tenant_id, uuid.UUID):
        return tenant_id
    return uuid.UUID(tenant_id)


def _event(row: UsageLedgerEvent) -> UsageEvent:
    return UsageEvent(
        tenant_id=str(row.tenant_id),
        event_type=row.event_type,
        occurred_at=row.occurred_at,
        quantity=row.quantity,
        metadata=deepcopy(row.metadata_),
        event_id=row.event_id,
    )
