from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.observability.metrics import (
    alert_dry_run,
    alert_rules,
    metric_contract,
    metrics,
    metrics_export_targets,
    render_prometheus_metrics,
)
from lead_sla_agent.observability.pii import PII_FIELD_NAMES

FORBIDDEN_LABEL_TERMS = {
    "lead_id",
    "conversation_id",
    "message",
    "message_text",
    "email",
    "phone",
    "provider_message_id",
    "provider_user_id",
    "transcript_text",
    "customer_name",
    "address",
    "secret",
    "token",
}


def test_metrics_export_targets_use_grafana_cloud_with_vps_fallback() -> None:
    targets = {target.environment: target for target in metrics_export_targets()}

    assert set(targets) == {"staging", "production"}
    for target in targets.values():
        assert target.backend == "grafana_cloud_prometheus"
        assert target.scrape_path == "/metrics"
        assert target.scrape_interval_seconds == 30
        assert target.route.startswith("grafana_alloy_remote_write_")
        assert target.fallback == "vps_prometheus_alertmanager"


def test_alert_rules_are_actionable_and_pii_free() -> None:
    metric_names = {definition.name for definition in metric_contract()}
    rules = alert_rules()

    assert {rule.name for rule in rules} >= {
        "first_response_latency_p95_high",
        "provider_send_failure_rate_high",
        "queue_depth_high",
        "api_error_rate_high",
        "unsafe_automation_blocks_spike",
        "sla_breach_detected",
    }
    for rule in rules:
        assert rule.metric in metric_names
        assert rule.threshold
        assert rule.duration
        assert rule.owner == "pilot_operator"
        assert rule.severity in {"page", "ticket"}
        assert rule.customer_impact
        assert rule.first_response_expectation
        assert rule.receiver == "pilot_operator"
        assert not (set(rule.labels) & PII_FIELD_NAMES)
        assert not (set(rule.labels) & FORBIDDEN_LABEL_TERMS)


def test_alert_dry_run_routes_to_pilot_operator() -> None:
    result = alert_dry_run("provider_send_failure_rate_high")

    assert result.status == "routed"
    assert result.receiver == "pilot_operator"
    assert result.route == "grafana_cloud_alerting:pilot_operator"


def test_prometheus_export_renders_text_without_pii_labels() -> None:
    metrics.reset()
    metrics.increment("provider_send_failure_total", 2)
    metrics.observe("first_response_latency_ms", 1250)

    rendered = render_prometheus_metrics(metrics)

    assert "# TYPE provider_send_failure_total counter" in rendered
    assert "provider_send_failure_total 2" in rendered
    assert "first_response_latency_ms_count 1" in rendered
    assert "first_response_latency_ms_sum 1250" in rendered
    for forbidden in FORBIDDEN_LABEL_TERMS:
        assert forbidden not in rendered


@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_prometheus_text() -> None:
    metrics.reset()
    metrics.increment("api_error_total", 1)
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "api_error_total 1" in response.text


def test_nfr_and_runbook_document_grafana_cloud_and_fallback() -> None:
    nfr = Path("docs/nfr.md").read_text(encoding="utf-8")
    runbook = Path("docs/runbook.md").read_text(encoding="utf-8")

    for required in (
        "Grafana Cloud",
        "Prometheus-compatible `/metrics`",
        "Grafana Alloy",
        "Prometheus + Alertmanager",
        "external uptime check",
    ):
        assert required in nfr
        assert required in runbook
