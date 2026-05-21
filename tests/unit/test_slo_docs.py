from __future__ import annotations

from pathlib import Path


def test_nfr_defines_required_pilot_slos_and_dashboard_panels() -> None:
    content = Path("docs/nfr.md").read_text(encoding="utf-8")

    for required in (
        "Production SLOs And Dashboard",
        "First response latency",
        "Provider send success",
        "Webhook intake success",
        "Review queue age",
        "Unsafe autonomous-send count",
        "first_response_latency_ms",
        "provider_send_failure_total",
        "api_error_total",
        "queue_depth",
        "unsafe_automation_block_total",
        "first_response_latency_p95_high",
        "provider_send_failure_rate_high",
        "api_error_rate_high",
        "queue_depth_high",
        "unsafe_automation_blocks_spike",
    ):
        assert required in content


def test_incident_drill_template_records_detection_mitigation_customer_impact_and_prevention() -> (
    None
):
    content = Path("docs/support/incident_template.md").read_text(encoding="utf-8")

    for required in (
        "Detected at:",
        "Mitigated at:",
        "Detection time:",
        "Mitigation time:",
        "Customer impact:",
        "Root cause:",
        "Prevention owner:",
        "Customer update template:",
    ):
        assert required in content


def test_support_runbook_links_severity_to_customer_update_templates() -> None:
    runbook = Path("docs/support/runbook.md").read_text(encoding="utf-8")
    templates = Path("docs/support/customer_templates.md").read_text(encoding="utf-8")

    assert "Customer Update Template Routing" in runbook
    for template_name in (
        "Provider Outage",
        "Provider Outage Resolved",
        "AI Safety Handoff",
        "AI Safety Incident",
    ):
        assert template_name in runbook
        assert template_name in templates
    assert "first update within 15 minutes" in runbook
    assert "first update within 1 business hour" in runbook
