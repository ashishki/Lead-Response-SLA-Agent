"""PostgreSQL-backed tenant configuration repository."""

from __future__ import annotations

import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.audit.events import AuditEventInput
from lead_sla_agent.db.audit_repository import AuditLogRepository
from lead_sla_agent.db.models import TenantConfig, TenantConfigAudit
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class TenantConfigPersistenceError(RuntimeError):
    """PII-safe tenant config persistence failure."""


class TenantConfigVersionConflict(RuntimeError):
    """Raised when a tenant config update uses a stale version."""


@dataclass(frozen=True)
class TenantConfigRecord:
    tenant_id: str
    version: int
    config: dict[str, Any]
    updated_at: str


@dataclass(frozen=True)
class TenantConfigAuditRecord:
    tenant_id: str
    event_type: str
    actor_id: str
    actor_role: str
    created_at: str
    event_metadata: dict[str, Any]


class TenantConfigRepository:
    """Versioned tenant configuration storage."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def get_config(self, tenant_id: uuid.UUID | str) -> TenantConfigRecord:
        tenant_uuid = _require_uuid_tenant_id(tenant_id)

        with self.tracer.start_as_current_span("db.tenant_config.get"):
            await apply_tenant_context(self.session, tenant_uuid)
            existing = await self._get_existing_config(tenant_uuid)
            if existing is not None:
                return _record(existing)

            created = TenantConfig(
                tenant_id=tenant_uuid,
                version=1,
                config=default_tenant_config(),
            )
            self.session.add(created)
            await _safe_flush(self.session)
            return _record(created)

    async def update_config(
        self,
        *,
        tenant_id: uuid.UUID | str,
        changes: dict[str, Any],
        actor_id: str,
        actor_role: str,
        approval_id: str | None,
        dangerous_change: bool,
        expected_version: int | None = None,
    ) -> TenantConfigRecord:
        tenant_uuid = _require_uuid_tenant_id(tenant_id)
        changed_fields = sorted(changes)

        with self.tracer.start_as_current_span("db.tenant_config.update"):
            await apply_tenant_context(self.session, tenant_uuid)
            previous = await self._get_existing_config(tenant_uuid)
            if previous is None:
                previous = TenantConfig(
                    tenant_id=tenant_uuid,
                    version=1,
                    config=default_tenant_config(),
                )
                self.session.add(previous)
                await _safe_flush(self.session)

            if expected_version is not None and previous.version != expected_version:
                raise TenantConfigVersionConflict("tenant config version conflict")

            next_config = deepcopy(previous.config)
            for field_name, value in changes.items():
                next_config[field_name] = value
            next_version = previous.version + 1

            statement = (
                update(TenantConfig)
                .where(
                    TenantConfig.tenant_id == tenant_uuid,
                    TenantConfig.version == previous.version,
                )
                .values(version=next_version, config=next_config, updated_at=func.now())
                .returning(TenantConfig)
            )
            result = await self.session.execute(statement)
            updated = result.scalar_one_or_none()
            if updated is None:
                raise TenantConfigVersionConflict("tenant config version conflict")

            audit = TenantConfigAudit(
                tenant_id=tenant_uuid,
                config_version=next_version,
                actor_id=actor_id,
                actor_role=actor_role,
                changed_fields=changed_fields,
                approval_id=approval_id,
                event_metadata={
                    "changed_fields": changed_fields,
                    "previous_version": previous.version,
                    "new_version": next_version,
                    "approval_id": approval_id,
                    "dangerous_change": dangerous_change,
                },
            )
            self.session.add(audit)
            await _safe_flush(self.session)
            await AuditLogRepository(self.session).append(
                AuditEventInput(
                    tenant_id=str(tenant_uuid),
                    actor_ref="operator:" + actor_id,
                    action="tenant_config.updated",
                    resource_type="tenant_config",
                    resource_id=str(tenant_uuid),
                    result="success",
                    payload={
                        "changed_fields": changed_fields,
                        "previous_version": previous.version,
                        "new_version": next_version,
                        "approval_id": approval_id,
                        "dangerous_change": dangerous_change,
                    },
                )
            )
            return _record(updated)

    async def history(self, tenant_id: uuid.UUID | str) -> list[TenantConfigAuditRecord]:
        tenant_uuid = _require_uuid_tenant_id(tenant_id)
        statement = (
            select(TenantConfigAudit)
            .where(TenantConfigAudit.tenant_id == tenant_uuid)
            .order_by(TenantConfigAudit.config_version)
        )

        with self.tracer.start_as_current_span("db.tenant_config.history"):
            await apply_tenant_context(self.session, tenant_uuid)
            result = await self.session.execute(statement)
            return [_audit_record(row) for row in result.scalars().all()]

    async def _get_existing_config(self, tenant_id: uuid.UUID) -> TenantConfig | None:
        statement = select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


def default_tenant_config() -> dict[str, Any]:
    return {
        "channels": ["website_form"],
        "business_hours": {"timezone": "America/Chicago", "days": ["mon-fri"], "hours": "08-18"},
        "required_fields": ["customer_name", "phone", "service_address_or_zip", "door_issue"],
        "max_turns": 6,
        "provider_settings": {"outbound_channel": "email"},
        "handoff_policy": ["unsupported_question", "booking_without_acceptance"],
        "unsafe_categories": ["pricing_commitment", "regulated_or_safety_advice"],
        "autonomous_send_enabled": True,
    }


def _require_uuid_tenant_id(tenant_id: uuid.UUID | str | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    if isinstance(tenant_id, uuid.UUID):
        return tenant_id
    return uuid.UUID(tenant_id)


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise TenantConfigPersistenceError("tenant config persistence failed") from None


def _record(row: TenantConfig) -> TenantConfigRecord:
    updated_at = _isoformat(row.updated_at)
    return TenantConfigRecord(
        tenant_id=str(row.tenant_id),
        version=row.version,
        config=deepcopy(row.config),
        updated_at=updated_at,
    )


def _audit_record(row: TenantConfigAudit) -> TenantConfigAuditRecord:
    return TenantConfigAuditRecord(
        tenant_id=str(row.tenant_id),
        event_type="tenant_config_updated",
        actor_id=row.actor_id,
        actor_role=row.actor_role,
        created_at=_isoformat(row.created_at),
        event_metadata=deepcopy(row.event_metadata),
    )


def _isoformat(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()
