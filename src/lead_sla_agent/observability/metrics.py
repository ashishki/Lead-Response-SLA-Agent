"""Metrics contract, Prometheus export, and alert routing definitions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

MetricKind = Literal["counter", "histogram", "gauge"]
AlertSeverity = Literal["page", "ticket"]
AlertReceiver = Literal["pilot_operator"]


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    kind: MetricKind
    labels: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class MetricsExportTarget:
    environment: str
    backend: str
    scrape_path: str
    scrape_interval_seconds: int
    route: str
    fallback: str


@dataclass(frozen=True)
class AlertRule:
    name: str
    metric: str
    expression: str
    threshold: str
    duration: str
    owner: str
    severity: AlertSeverity
    customer_impact: str
    first_response_expectation: str
    receiver: AlertReceiver
    labels: tuple[str, ...]


@dataclass(frozen=True)
class AlertDryRunResult:
    alert_name: str
    receiver: AlertReceiver
    status: str
    route: str


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
        name="api_error_total",
        kind="counter",
        labels=("component", "status_class"),
        description="API and worker request errors grouped by component and status class.",
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
        name="unsafe_automation_block_total",
        kind="counter",
        labels=("tenant_hash", "reason"),
        description="Autonomous sends blocked by policy, approval, or unsafe-message gates.",
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
    "api_error_total": "greater than 1 percent of API requests for 10 minutes",
    "sla_breach_total": "any sustained increase above pilot baseline for 15 minutes",
    "retrieval_freshness_age_hours": "greater than 24 hours",
    "insufficient_evidence_total": "greater than 20 percent of inbound leads for 30 minutes",
    "tool_call_failure_total": "greater than 5 percent of tool calls for 10 minutes",
    "unsafe_automation_block_total": "any unexpected autonomous-send block spike for 10 minutes",
    "queue_depth": "greater than 100 pending jobs or growing for 15 minutes",
}

METRICS_EXPORT_TARGETS: tuple[MetricsExportTarget, ...] = (
    MetricsExportTarget(
        environment="staging",
        backend="grafana_cloud_prometheus",
        scrape_path="/metrics",
        scrape_interval_seconds=30,
        route="grafana_alloy_remote_write_staging",
        fallback="vps_prometheus_alertmanager",
    ),
    MetricsExportTarget(
        environment="production",
        backend="grafana_cloud_prometheus",
        scrape_path="/metrics",
        scrape_interval_seconds=30,
        route="grafana_alloy_remote_write_production",
        fallback="vps_prometheus_alertmanager",
    ),
)

ALERT_RULES: tuple[AlertRule, ...] = (
    AlertRule(
        name="first_response_latency_p95_high",
        metric="first_response_latency_ms",
        expression="histogram_quantile(0.95, first_response_latency_ms)",
        threshold="> 30000 ms",
        duration="10m",
        owner="pilot_operator",
        severity="page",
        customer_impact="leads are waiting too long for first response",
        first_response_expectation="acknowledge within 10 minutes",
        receiver="pilot_operator",
        labels=("tenant_hash", "channel"),
    ),
    AlertRule(
        name="provider_send_failure_rate_high",
        metric="provider_send_failure_total",
        expression=(
            "rate(provider_send_failure_total[10m]) / rate(provider_send_attempt_total[10m])"
        ),
        threshold="> 2 percent",
        duration="10m",
        owner="pilot_operator",
        severity="page",
        customer_impact="approved replies may not reach customers",
        first_response_expectation="inspect provider dashboard within 10 minutes",
        receiver="pilot_operator",
        labels=("provider", "failure_reason"),
    ),
    AlertRule(
        name="queue_depth_high",
        metric="queue_depth",
        expression="queue_depth",
        threshold="> 100 jobs or growing for 15m",
        duration="15m",
        owner="pilot_operator",
        severity="page",
        customer_impact="lead processing may be delayed",
        first_response_expectation="inspect worker and Redis within 10 minutes",
        receiver="pilot_operator",
        labels=("queue_name",),
    ),
    AlertRule(
        name="api_error_rate_high",
        metric="api_error_total",
        expression="rate(api_error_total[10m])",
        threshold="> 1 percent",
        duration="10m",
        owner="pilot_operator",
        severity="page",
        customer_impact="webhooks or operator actions may fail",
        first_response_expectation="inspect API logs and health within 10 minutes",
        receiver="pilot_operator",
        labels=("component", "status_class"),
    ),
    AlertRule(
        name="unsafe_automation_blocks_spike",
        metric="unsafe_automation_block_total",
        expression="increase(unsafe_automation_block_total[10m])",
        threshold="unexpected spike above pilot baseline",
        duration="10m",
        owner="pilot_operator",
        severity="ticket",
        customer_impact="more replies require manual review before sending",
        first_response_expectation="review policy and recent prompts within 1 business day",
        receiver="pilot_operator",
        labels=("tenant_hash", "reason"),
    ),
    AlertRule(
        name="sla_breach_detected",
        metric="sla_breach_total",
        expression="increase(sla_breach_total[15m])",
        threshold="> 0 sustained above pilot baseline",
        duration="15m",
        owner="pilot_operator",
        severity="page",
        customer_impact="buyer may lose leads due to slow response",
        first_response_expectation="triage queue and provider status within 10 minutes",
        receiver="pilot_operator",
        labels=("tenant_hash", "channel"),
    ),
)


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


def metrics_export_targets() -> tuple[MetricsExportTarget, ...]:
    return METRICS_EXPORT_TARGETS


def alert_rules() -> tuple[AlertRule, ...]:
    return ALERT_RULES


def alert_dry_run(alert_name: str) -> AlertDryRunResult:
    for rule in ALERT_RULES:
        if rule.name == alert_name:
            return AlertDryRunResult(
                alert_name=rule.name,
                receiver=rule.receiver,
                status="routed",
                route="grafana_cloud_alerting:pilot_operator",
            )
    raise KeyError("unknown alert rule")


def render_prometheus_metrics(source: InMemoryMetrics) -> str:
    lines: list[str] = []
    definitions_by_name = {definition.name: definition for definition in METRIC_DEFINITIONS}
    for metric_name, value in sorted(source.counters.items()):
        definition = definitions_by_name.get(metric_name)
        description = definition.description if definition else "Runtime counter."
        lines.extend(
            [
                f"# HELP {metric_name} {description}",
                f"# TYPE {metric_name} counter",
                f"{metric_name} {value}",
            ]
        )
    for metric_name, values in sorted(source.histograms.items()):
        definition = definitions_by_name.get(metric_name)
        description = definition.description if definition else "Runtime histogram."
        lines.extend(
            [
                f"# HELP {metric_name} {description}",
                f"# TYPE {metric_name} histogram",
                f"{metric_name}_count {len(values)}",
                f"{metric_name}_sum {sum(values)}",
            ]
        )
    return "\n".join(lines) + ("\n" if lines else "")


metrics = InMemoryMetrics()
