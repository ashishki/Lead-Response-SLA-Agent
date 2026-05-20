"""Small metrics facade used until a backend exporter is configured."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

MetricKind = Literal["counter", "histogram", "gauge"]


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    kind: MetricKind
    labels: tuple[str, ...]
    description: str


METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        name="first_response_latency_ms",
        kind="histogram",
        labels=("tenant_hash", "channel"),
        description="Milliseconds from inbound lead receipt to first outbound response.",
    ),
    MetricDefinition(
        name="retrieval_latency_ms",
        kind="histogram",
        labels=("tenant_hash", "corpus_version"),
        description="Milliseconds spent retrieving approved evidence for a tenant query.",
    ),
    MetricDefinition(
        name="retrieval_freshness_age_hours",
        kind="histogram",
        labels=("tenant_hash", "corpus_version"),
        description="Age in hours of the active retrieval index.",
    ),
    MetricDefinition(
        name="provider_send_failure_total",
        kind="counter",
        labels=("provider", "failure_reason"),
        description="Outbound provider sends that failed or timed out.",
    ),
    MetricDefinition(
        name="sla_breach_total",
        kind="counter",
        labels=("tenant_hash", "channel"),
        description="Leads that breached first-response SLA.",
    ),
    MetricDefinition(
        name="insufficient_evidence_total",
        kind="counter",
        labels=("tenant_hash", "reason"),
        description="Customer questions routed to handoff due to insufficient approved evidence.",
    ),
    MetricDefinition(
        name="tool_call_failure_total",
        kind="counter",
        labels=("tool_name", "failure_reason"),
        description="Tool calls rejected, failed, or routed to fallback.",
    ),
    MetricDefinition(
        name="queue_depth",
        kind="gauge",
        labels=("queue_name",),
        description="Current depth of worker queues and retry queues.",
    ),
    MetricDefinition(
        name="health_dependency_status",
        kind="gauge",
        labels=("dependency",),
        description="Dependency health status encoded for dashboards and alerts.",
    ),
)

ALERT_THRESHOLDS = {
    "first_response_latency_ms_p95": "greater than 30000 for 10 minutes",
    "provider_send_failure_total": "greater than 2 percent of sends for 10 minutes",
    "sla_breach_total": "any sustained increase above pilot baseline for 15 minutes",
    "retrieval_freshness_age_hours": "greater than 24 hours",
    "insufficient_evidence_total": "greater than 20 percent of inbound leads for 30 minutes",
    "tool_call_failure_total": "greater than 5 percent of tool calls for 10 minutes",
    "queue_depth": "greater than 100 pending jobs or growing for 15 minutes",
}


@dataclass
class InMemoryMetrics:
    """In-process metrics collector for deterministic unit tests."""

    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    histograms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def observe(self, name: str, value: float) -> None:
        self.histograms[name].append(value)

    def reset(self) -> None:
        self.counters.clear()
        self.histograms.clear()


def metric_contract() -> tuple[MetricDefinition, ...]:
    return METRIC_DEFINITIONS


metrics = InMemoryMetrics()
