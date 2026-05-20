from __future__ import annotations

from datetime import UTC, datetime

import pytest

from lead_sla_agent.billing.usage import (
    PRICING_PACKAGE_MAPPING_VERSION,
    USAGE_SCHEMA_VERSION,
    UsageEvent,
    UsageMeter,
)


def test_usage_events_are_tenant_scoped_and_append_only() -> None:
    meter = UsageMeter()
    event = UsageEvent(
        tenant_id="tenant-1",
        event_type="lead_processed",
        occurred_at=datetime(2026, 5, 20, tzinfo=UTC),
        metadata={"channel": "website_form"},
    )

    recorded = meter.record_event(event)

    assert recorded == event
    assert meter.events == (event,)
    with pytest.raises(AttributeError):
        meter.events.append(event)  # type: ignore[attr-defined]


def test_monthly_usage_export_counts_billing_dimensions_without_pii() -> None:
    meter = UsageMeter()
    for event in _usage_events():
        meter.record_event(event)

    export = meter.monthly_export("tenant-1", 2026, 5)

    assert export["schema_version"] == USAGE_SCHEMA_VERSION
    assert export["pricing_mapping_version"] == PRICING_PACKAGE_MAPPING_VERSION
    assert export["tenant_id"] == "tenant-1"
    assert export["period"] == "2026-05"
    assert export["usage"] == {
        "leads_processed": 2,
        "ai_assisted_replies": 1,
        "provider_sends": 2,
        "review_tasks": 1,
        "bookings": 1,
        "active_channels": ["sms", "website_form"],
        "provider_sends_by_provider": {"email": 1, "sms": 1},
    }
    serialized = str(export)
    assert "customer" not in serialized.lower()
    assert "phone" not in serialized.lower()
    assert "email@example" not in serialized


def test_pricing_experiments_map_to_usage_exports() -> None:
    meter = UsageMeter(_usage_events())

    mapping = meter.monthly_export("tenant-1", 2026, 5)["pricing_experiment_mapping"]

    assert mapping["Recovery Pilot"] == {
        "primary_metric": "bookings",
        "bookings": 1,
        "review_tasks": 1,
    }
    assert mapping["Booked-Lead Share"] == {
        "primary_metric": "bookings",
        "billable_booked_leads": 1,
    }
    assert mapping["Dispatcher Assist"] == {
        "primary_metric": "leads_processed",
        "leads_processed": 2,
        "ai_assisted_replies": 1,
        "active_channels": ["sms", "website_form"],
    }


def test_usage_meter_rejects_pii_metadata() -> None:
    meter = UsageMeter()

    with pytest.raises(ValueError, match="usage metadata contains unsupported or PII fields"):
        meter.record_event(
            UsageEvent(
                tenant_id="tenant-1",
                event_type="lead_processed",
                occurred_at=datetime(2026, 5, 20, tzinfo=UTC),
                metadata={"email": "customer@example.test"},
            )
        )


def test_usage_export_excludes_other_tenants_and_months() -> None:
    meter = UsageMeter(_usage_events())

    tenant_2 = meter.monthly_export("tenant-2", 2026, 5)
    tenant_1_june = meter.monthly_export("tenant-1", 2026, 6)

    assert tenant_2["usage"]["leads_processed"] == 1
    assert tenant_2["usage"]["bookings"] == 0
    assert tenant_1_june["usage"]["leads_processed"] == 1
    assert tenant_1_june["usage"]["provider_sends"] == 0


def _usage_events() -> list[UsageEvent]:
    may = datetime(2026, 5, 20, tzinfo=UTC)
    june = datetime(2026, 6, 1, tzinfo=UTC)
    return [
        UsageEvent("tenant-1", "lead_processed", may, metadata={"channel": "website_form"}),
        UsageEvent("tenant-1", "lead_processed", may, metadata={"channel": "sms"}),
        UsageEvent("tenant-1", "ai_assisted_reply", may, metadata={"channel": "sms"}),
        UsageEvent("tenant-1", "provider_send", may, metadata={"provider": "sms"}),
        UsageEvent("tenant-1", "provider_send", may, metadata={"provider": "email"}),
        UsageEvent("tenant-1", "review_task", may, metadata={"source": "unsupported_question"}),
        UsageEvent("tenant-1", "booking", may, metadata={"outcome": "booked"}),
        UsageEvent("tenant-1", "active_channel", may, metadata={"channel": "website_form"}),
        UsageEvent("tenant-1", "active_channel", may, metadata={"channel": "sms"}),
        UsageEvent("tenant-2", "lead_processed", may, metadata={"channel": "website_form"}),
        UsageEvent("tenant-1", "lead_processed", june, metadata={"channel": "website_form"}),
    ]
