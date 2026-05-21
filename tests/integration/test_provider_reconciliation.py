from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from lead_sla_agent.operator.provider_reconciliation import (
    ExpectedProviderRecord,
    ObservedProviderRecord,
    reconcile_provider_records,
)
from lead_sla_agent.tools.calendar import BookingResult
from lead_sla_agent.tools.crm import CRMWriteResult
from lead_sla_agent.tools.messaging import MessageSendResult

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def test_calendar_booking_reconciliation_reports_missing_duplicate_and_stale_records() -> None:
    now = datetime.now(tz=UTC)
    expected = [
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="calendar_booking",
            idempotency_key="lead-1:slot-1",
        ),
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="calendar_booking",
            idempotency_key="lead-2:slot-2",
        ),
    ]
    observed = [
        ObservedProviderRecord.from_booking_result(
            TENANT_ID,
            BookingResult(
                booking_id="booking-1",
                status="booked",
                idempotency_key="lead-1:slot-1",
            ),
            observed_at=now - timedelta(hours=2),
        ),
        ObservedProviderRecord.from_booking_result(
            TENANT_ID,
            BookingResult(
                booking_id="booking-1-duplicate",
                status="booked",
                idempotency_key="lead-1:slot-1",
            ),
            observed_at=now,
        ),
    ]

    report = reconcile_provider_records(expected, observed, now=now, stale_after=timedelta(hours=1))

    discrepancies = [
        (item.record_type, item.idempotency_key, item.discrepancy_type)
        for item in report.discrepancies
    ]
    assert discrepancies == [
        ("calendar_booking", "lead-1:slot-1", "duplicate"),
        ("calendar_booking", "lead-1:slot-1", "stale"),
        ("calendar_booking", "lead-2:slot-2", "missing"),
    ]


def test_crm_reconciliation_uses_remote_record_and_source_event_id_without_pii() -> None:
    expected = [
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="crm_lead",
            idempotency_key="source-event-1",
            provider_record_id="crm-record-1",
        )
    ]
    observed = [
        ObservedProviderRecord.from_crm_result(
            TENANT_ID,
            CRMWriteResult(
                remote_record_id="",
                status="retry_required",
                idempotency_key="source-event-1",
                failure_reason="provider_timeout",
                retry_required=True,
            ),
        )
    ]

    report = reconcile_provider_records(expected, observed)

    assert len(report.discrepancies) == 1
    discrepancy = report.discrepancies[0]
    assert discrepancy.record_type == "crm_lead"
    assert discrepancy.idempotency_key == "source-event-1"
    assert discrepancy.discrepancy_type == "failed"
    assert discrepancy.failure_reason == "provider_timeout"
    assert "private@example.test" not in str(report.operator_actions())


def test_message_reconciliation_covers_email_whatsapp_and_telegram_statuses() -> None:
    expected = [
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="message_send",
            idempotency_key="email:key",
            channel="email",
        ),
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="message_send",
            idempotency_key="whatsapp:key",
            channel="whatsapp",
        ),
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="message_send",
            idempotency_key="telegram:key",
            channel="telegram",
        ),
    ]
    observed = [
        ObservedProviderRecord.from_message_result(
            TENANT_ID,
            MessageSendResult(
                provider_message_id="postmark-msg-1",
                status="sent",
                latency_ms=1,
                redacted_preview="[secret-redacted]",
                idempotency_key="email:key",
                provider="postmark_email",
                channel="email",
            ),
        ),
        ObservedProviderRecord.from_message_result(
            TENANT_ID,
            MessageSendResult(
                provider_message_id="",
                status="rate_limited",
                latency_ms=1,
                redacted_preview="[secret-redacted]",
                failure_reason="rate_limited",
                idempotency_key="whatsapp:key",
                provider="twilio_whatsapp",
                channel="whatsapp",
                rate_limited=True,
            ),
        ),
    ]

    report = reconcile_provider_records(expected, observed)

    assert [(item.channel, item.discrepancy_type) for item in report.discrepancies] == [
        ("whatsapp", "rate_limited"),
        ("telegram", "missing"),
    ]
    assert report.operator_actions() == [
        {
            "action": "retry_or_handoff",
            "tenant_id": str(TENANT_ID),
            "record_type": "message_send",
            "idempotency_key": "whatsapp:key",
            "discrepancy_type": "rate_limited",
            "provider_record_id": "",
            "channel": "whatsapp",
            "failure_reason": "rate_limited",
        },
        {
            "action": "retry_or_handoff",
            "tenant_id": str(TENANT_ID),
            "record_type": "message_send",
            "idempotency_key": "telegram:key",
            "discrepancy_type": "missing",
            "provider_record_id": "",
            "channel": "telegram",
            "failure_reason": "",
        },
    ]


def test_reconciliation_is_tenant_scoped() -> None:
    other_tenant = uuid.UUID("00000000-0000-4000-8000-000000000002")
    expected = [
        ExpectedProviderRecord(
            tenant_id=TENANT_ID,
            record_type="message_send",
            idempotency_key="same-key",
            channel="email",
        )
    ]
    observed = [
        ObservedProviderRecord(
            tenant_id=other_tenant,
            record_type="message_send",
            idempotency_key="same-key",
            provider_record_id="postmark-other",
            status="sent",
            observed_at=datetime.now(tz=UTC),
            channel="email",
        )
    ]

    report = reconcile_provider_records(expected, observed)

    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].discrepancy_type == "missing"
    assert report.discrepancies[0].tenant_id == TENANT_ID
