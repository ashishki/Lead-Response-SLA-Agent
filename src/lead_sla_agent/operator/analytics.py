"""Pilot analytics for operator ROI reporting."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class PilotLeadEvent:
    tenant_id: str
    lead_id: str
    inbound_at: datetime
    first_response_at: datetime | None
    response_mode: str
    human_review_required: bool = False
    outcome_label: str | None = None
    provider_send_failed: bool = False


class PilotAnalyticsStore:
    def __init__(self, events: list[PilotLeadEvent] | None = None) -> None:
        self.events = events if events is not None else []

    def add_event(self, event: PilotLeadEvent) -> None:
        self.events.append(event)

    def metrics(self, tenant_id: str, start_date: date, end_date: date) -> dict[str, Any]:
        events = self._events_for_range(tenant_id, start_date, end_date)
        latencies = [
            (event.first_response_at - event.inbound_at).total_seconds() * 1000
            for event in events
            if event.first_response_at is not None
        ]
        total = len(events)
        automation_success_count = sum(
            1
            for event in events
            if event.response_mode == "automated"
            and not event.human_review_required
            and not event.provider_send_failed
        )
        human_review_count = sum(1 for event in events if event.human_review_required)
        provider_send_failures = sum(1 for event in events if event.provider_send_failed)
        booked_labels = sum(1 for event in events if event.outcome_label == "booked")

        return {
            "tenant_id": tenant_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "lead_count": total,
            "first_response_latency_p50_ms": _p50(latencies),
            "first_response_latency_p95_ms": _p95(latencies),
            "automation_success_count": automation_success_count,
            "automation_success_rate": _rate(automation_success_count, total),
            "human_review_count": human_review_count,
            "human_review_rate": _rate(human_review_count, total),
            "booked_labels": booked_labels,
            "provider_send_failures": provider_send_failures,
        }

    def weekly_report_payload(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        metrics = self.metrics(tenant_id, start_date, end_date)
        return {
            "metrics": metrics,
            "weekly_report": weekly_report_markdown(metrics),
        }

    def _events_for_range(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> list[PilotLeadEvent]:
        return [
            event
            for event in self.events
            if event.tenant_id == tenant_id and start_date <= event.inbound_at.date() <= end_date
        ]


def weekly_report_markdown(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Pilot Weekly Report",
            "",
            f"Window: {metrics['start_date']} to {metrics['end_date']}",
            f"Lead count: {metrics['lead_count']}",
            f"First-response latency p50: {metrics['first_response_latency_p50_ms']} ms",
            f"First-response latency p95: {metrics['first_response_latency_p95_ms']} ms",
            f"Automation success rate: {metrics['automation_success_rate']:.2f}",
            f"Human-review rate: {metrics['human_review_rate']:.2f}",
            f"Booked outcomes: {metrics['booked_labels']}",
            f"Provider send failures: {metrics['provider_send_failures']}",
        ]
    )


def _p50(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return float(ordered[index])


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
