"""PII-safe reconciliation for external provider records."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from lead_sla_agent.tools.calendar import BookingResult
from lead_sla_agent.tools.crm import CRMWriteResult
from lead_sla_agent.tools.messaging import MessageSendResult

ProviderRecordType = Literal["calendar_booking", "crm_lead", "message_send"]
DiscrepancyType = Literal["missing", "duplicate", "failed", "rate_limited", "stale"]


@dataclass(frozen=True)
class ExpectedProviderRecord:
    tenant_id: uuid.UUID
    record_type: ProviderRecordType
    idempotency_key: str
    provider_record_id: str | None = None
    channel: str | None = None


@dataclass(frozen=True)
class ObservedProviderRecord:
    tenant_id: uuid.UUID
    record_type: ProviderRecordType
    idempotency_key: str
    provider_record_id: str
    status: str
    observed_at: datetime
    channel: str | None = None
    failure_reason: str | None = None

    @classmethod
    def from_booking_result(
        cls,
        tenant_id: uuid.UUID,
        result: BookingResult,
        observed_at: datetime | None = None,
    ) -> ObservedProviderRecord:
        return cls(
            tenant_id=tenant_id,
            record_type="calendar_booking",
            idempotency_key=result.idempotency_key or "",
            provider_record_id=result.booking_id,
            status=result.status,
            observed_at=observed_at or datetime.now(tz=UTC),
            failure_reason=result.failure_reason,
        )

    @classmethod
    def from_crm_result(
        cls,
        tenant_id: uuid.UUID,
        result: CRMWriteResult,
        observed_at: datetime | None = None,
    ) -> ObservedProviderRecord:
        return cls(
            tenant_id=tenant_id,
            record_type="crm_lead",
            idempotency_key=result.idempotency_key,
            provider_record_id=result.remote_record_id,
            status=result.status,
            observed_at=observed_at or datetime.now(tz=UTC),
            failure_reason=result.failure_reason,
        )

    @classmethod
    def from_message_result(
        cls,
        tenant_id: uuid.UUID,
        result: MessageSendResult,
        observed_at: datetime | None = None,
    ) -> ObservedProviderRecord:
        return cls(
            tenant_id=tenant_id,
            record_type="message_send",
            idempotency_key=result.idempotency_key or "",
            provider_record_id=result.provider_message_id,
            status=result.status,
            observed_at=observed_at or datetime.now(tz=UTC),
            channel=result.channel,
            failure_reason=result.failure_reason,
        )


@dataclass(frozen=True)
class ProviderDiscrepancy:
    tenant_id: uuid.UUID
    record_type: ProviderRecordType
    idempotency_key: str
    discrepancy_type: DiscrepancyType
    provider_record_id: str | None = None
    channel: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True)
class ReconciliationReport:
    discrepancies: tuple[ProviderDiscrepancy, ...]

    def operator_actions(self) -> list[dict[str, str]]:
        return [
            {
                "action": "retry_or_handoff",
                "tenant_id": str(discrepancy.tenant_id),
                "record_type": discrepancy.record_type,
                "idempotency_key": discrepancy.idempotency_key,
                "discrepancy_type": discrepancy.discrepancy_type,
                "provider_record_id": discrepancy.provider_record_id or "",
                "channel": discrepancy.channel or "",
                "failure_reason": discrepancy.failure_reason or "",
            }
            for discrepancy in self.discrepancies
        ]


def reconcile_provider_records(
    expected: list[ExpectedProviderRecord],
    observed: list[ObservedProviderRecord],
    *,
    now: datetime | None = None,
    stale_after: timedelta = timedelta(hours=1),
) -> ReconciliationReport:
    now = now or datetime.now(tz=UTC)
    discrepancies: list[ProviderDiscrepancy] = []
    observed_by_key: dict[
        tuple[uuid.UUID, ProviderRecordType, str, str | None],
        list[ObservedProviderRecord],
    ] = {}
    for record in observed:
        observed_by_key.setdefault(_record_key(record), []).append(record)

    for expected_record in expected:
        matches = observed_by_key.get(_record_key(expected_record), [])
        if not matches:
            discrepancies.append(_discrepancy(expected_record, "missing"))
            continue
        if len(matches) > 1:
            discrepancies.append(_discrepancy(expected_record, "duplicate", matches[0]))

        for observed_record in matches:
            if observed_record.status in {"failed", "retry_required", "human_review_required"}:
                discrepancies.append(_discrepancy(expected_record, "failed", observed_record))
            if observed_record.status == "rate_limited":
                discrepancies.append(_discrepancy(expected_record, "rate_limited", observed_record))
            if now - observed_record.observed_at > stale_after:
                discrepancies.append(_discrepancy(expected_record, "stale", observed_record))

    return ReconciliationReport(discrepancies=tuple(discrepancies))


def _record_key(
    record: ExpectedProviderRecord | ObservedProviderRecord,
) -> tuple[uuid.UUID, ProviderRecordType, str, str | None]:
    return (record.tenant_id, record.record_type, record.idempotency_key, record.channel)


def _discrepancy(
    expected: ExpectedProviderRecord,
    discrepancy_type: DiscrepancyType,
    observed: ObservedProviderRecord | None = None,
) -> ProviderDiscrepancy:
    return ProviderDiscrepancy(
        tenant_id=expected.tenant_id,
        record_type=expected.record_type,
        idempotency_key=expected.idempotency_key,
        discrepancy_type=discrepancy_type,
        provider_record_id=(
            observed.provider_record_id if observed else expected.provider_record_id
        ),
        channel=expected.channel,
        failure_reason=observed.failure_reason if observed else None,
    )
