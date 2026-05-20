"""Lead outcome label storage."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import OutcomeLabel
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class OutcomeStore:
    """Lead outcome label store with in-memory and PostgreSQL-backed modes."""

    def __init__(
        self,
        labels: list[dict[str, Any]] | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self.labels = labels if labels is not None else []
        self.session = session
        self.tracer = get_tracer(__name__)

    async def add_label(
        self,
        tenant_id: str | uuid.UUID,
        lead_id: str | uuid.UUID,
        label: str,
        labeled_on: date,
    ) -> dict[str, Any]:
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            lead_uuid = _require_uuid(lead_id, "lead_id")
            with self.tracer.start_as_current_span("db.outcome_label.create"):
                await apply_tenant_context(self.session, tenant_uuid)
                row = OutcomeLabel(
                    tenant_id=tenant_uuid,
                    lead_id=lead_uuid,
                    label=label,
                    labeled_on=labeled_on,
                )
                self.session.add(row)
                await _safe_flush(self.session)
            return _label_row(row)

        row = {
            "tenant_id": str(tenant_id),
            "lead_id": str(lead_id),
            "label": label,
            "labeled_on": labeled_on.isoformat(),
        }
        self.labels.append(row)
        return row

    async def query_labels(
        self,
        tenant_id: str | uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            statement = (
                select(OutcomeLabel)
                .where(
                    OutcomeLabel.tenant_id == tenant_uuid,
                    OutcomeLabel.labeled_on >= start_date,
                    OutcomeLabel.labeled_on <= end_date,
                )
                .order_by(OutcomeLabel.labeled_on, OutcomeLabel.id)
            )
            with self.tracer.start_as_current_span("db.outcome_label.query"):
                await apply_tenant_context(self.session, tenant_uuid)
                result = await self.session.execute(statement)
            return [_label_row(row) for row in result.scalars().all()]

        tenant_key = str(tenant_id)
        return [
            row
            for row in self.labels
            if row["tenant_id"] == tenant_key
            and start_date <= date.fromisoformat(row["labeled_on"]) <= end_date
        ]


def _require_uuid_tenant_id(tenant_id: str | uuid.UUID | None) -> uuid.UUID:
    return _require_uuid(tenant_id, "tenant_id")


def _require_uuid(value: str | uuid.UUID | None, field_name: str) -> uuid.UUID:
    if value is None:
        raise ValueError(field_name + " is required")
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(value)


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise RuntimeError("repository persistence failed") from None


def _label_row(row: OutcomeLabel) -> dict[str, Any]:
    return {
        "tenant_id": str(row.tenant_id),
        "lead_id": str(row.lead_id),
        "label": row.label,
        "labeled_on": row.labeled_on.isoformat(),
    }
