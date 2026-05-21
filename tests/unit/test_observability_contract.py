from __future__ import annotations

from pathlib import Path

from lead_sla_agent.observability.metrics import ALERT_THRESHOLDS, metric_contract
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
}
REQUIRED_METRICS = {
    "first_response_latency_ms",
    "retrieval_latency_ms",
    "retrieval_freshness_age_hours",
    "provider_send_failure_total",
    "api_error_total",
    "sla_breach_total",
    "insufficient_evidence_total",
    "tool_call_failure_total",
    "unsafe_automation_block_total",
    "queue_depth",
    "health_dependency_status",
}


def test_metric_contract_has_stable_pii_free_names_and_labels() -> None:
    definitions = metric_contract()
    metric_names = {definition.name for definition in definitions}

    assert metric_names == REQUIRED_METRICS
    assert len(metric_names) == len(definitions)
    for definition in definitions:
        assert definition.kind in {"counter", "histogram", "gauge"}
        assert definition.description
        assert not (set(definition.labels) & PII_FIELD_NAMES)
        assert not (set(definition.labels) & FORBIDDEN_LABEL_TERMS)


def test_alert_thresholds_cover_required_metrics() -> None:
    assert set(ALERT_THRESHOLDS) >= {
        "first_response_latency_ms_p95",
        "provider_send_failure_total",
        "api_error_total",
        "sla_breach_total",
        "retrieval_freshness_age_hours",
        "insufficient_evidence_total",
        "tool_call_failure_total",
        "unsafe_automation_block_total",
        "queue_depth",
    }
    assert all(ALERT_THRESHOLDS.values())


def test_nfr_documents_metrics_and_alert_thresholds() -> None:
    content = Path("docs/nfr.md").read_text(encoding="utf-8")

    for metric_name in REQUIRED_METRICS:
        assert metric_name in content
    assert "PII-free labels" in content
    assert "p95 greater than 30000 ms" in content
    assert "greater than 24 hours" in content


def test_runbook_documents_required_incident_paths() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    for section in (
        "Provider Outage",
        "Retrieval Regression",
        "Queue Backlog",
        "Webhook Signature Failures",
    ):
        assert section in content
    for forbidden in ("phone numbers", "emails", "message text", "provider message IDs"):
        assert forbidden in content
