"""Tenant-scoped append-only usage metering."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lead_sla_agent.observability.pii import PII_FIELD_NAMES

USAGE_SCHEMA_VERSION = "usage-export-v1"
USAGE_EVENT_TYPES = frozenset(
    {
        "lead_processed",
        "ai_assisted_reply",
        "provider_send",
        "review_task",
        "booking",
        "active_channel",
    }
)
ALLOWED_METADATA_KEYS = frozenset(
    {
        "channel",
        "provider",
        "pricing_package",
        "outcome",
        "source",
        "failure_reason",
    }
)


@dataclass(frozen=True)
class UsageEvent:
    tenant_id: str
    event_type: str
    occurred_at: datetime
    quantity: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


class UsageMeter:
    def __init__(self, events: list[UsageEvent] | None = None) -> None:
        self._events = list(events or [])

    @property
    def events(self) -> tuple[UsageEvent, ...]:
        return tuple(self._events)

    def record_event(self, event: UsageEvent) -> UsageEvent:
        if event.event_type not in USAGE_EVENT_TYPES:
            raise ValueError("unsupported usage event type")
        _validate_metadata(event.metadata)
        self._events.append(event)
        return event

    def monthly_export(self, tenant_id: str, year: int, month: int) -> dict[str, Any]:
        events = [
            event
            for event in self._events
            if event.tenant_id == tenant_id
            and event.occurred_at.year == year
            and event.occurred_at.month == month
        ]
        counts = Counter[str]()
        active_channels: set[str] = set()
        provider_sends_by_provider = Counter[str]()
        for event in events:
            counts[event.event_type] += event.quantity
            channel = event.metadata.get("channel")
            provider = event.metadata.get("provider")
            if event.event_type == "active_channel" and isinstance(channel, str):
                active_channels.add(channel)
            if event.event_type == "provider_send" and isinstance(provider, str):
                provider_sends_by_provider[provider] += event.quantity

        return {
            "schema_version": USAGE_SCHEMA_VERSION,
            "tenant_id": tenant_id,
            "period": f"{year:04d}-{month:02d}",
            "usage": {
                "leads_processed": counts["lead_processed"],
                "ai_assisted_replies": counts["ai_assisted_reply"],
                "provider_sends": counts["provider_send"],
                "review_tasks": counts["review_task"],
                "bookings": counts["booking"],
                "active_channels": sorted(active_channels),
                "provider_sends_by_provider": dict(sorted(provider_sends_by_provider.items())),
            },
            "pricing_experiment_mapping": pricing_experiment_mapping(counts, active_channels),
        }


def pricing_experiment_mapping(counts: Counter[str], active_channels: set[str]) -> dict[str, Any]:
    return {
        "Recovery Pilot": {
            "primary_metric": "bookings",
            "bookings": counts["booking"],
            "review_tasks": counts["review_task"],
        },
        "Booked-Lead Share": {
            "primary_metric": "bookings",
            "billable_booked_leads": counts["booking"],
        },
        "Dispatcher Assist": {
            "primary_metric": "leads_processed",
            "leads_processed": counts["lead_processed"],
            "ai_assisted_replies": counts["ai_assisted_reply"],
            "active_channels": sorted(active_channels),
        },
    }


def _validate_metadata(metadata: dict[str, Any]) -> None:
    disallowed_keys = set(metadata) - ALLOWED_METADATA_KEYS
    pii_keys = set(metadata) & PII_FIELD_NAMES
    if disallowed_keys or pii_keys:
        rejected = sorted(disallowed_keys | pii_keys)
        raise ValueError(
            "usage metadata contains unsupported or PII fields: " + ", ".join(rejected)
        )
