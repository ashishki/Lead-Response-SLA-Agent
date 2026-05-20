from __future__ import annotations

from pathlib import Path


def test_support_runbook_defines_severity_sla_and_escalation() -> None:
    content = Path("docs/support/runbook.md").read_text(encoding="utf-8")

    for severity in ("Sev1", "Sev2", "Sev3", "Sev4"):
        assert severity in content
    assert "15 minutes" in content
    assert "1 business hour" in content
    assert "Escalation" in content
    assert "Post-Incident Review" in content
    assert "Do not paste customer names" in content


def test_incident_template_has_required_post_incident_fields() -> None:
    content = Path("docs/support/incident_template.md").read_text(encoding="utf-8")

    for field in (
        "Incident ID:",
        "Severity:",
        "Tenant hash:",
        "Started at:",
        "Summary",
        "Impact",
        "Timeline",
        "Root Cause",
        "Prevention Tasks",
    ):
        assert field in content
    assert "provider message IDs" in content


def test_customer_templates_cover_provider_outage_and_ai_safety_handoff() -> None:
    content = Path("docs/support/customer_templates.md").read_text(encoding="utf-8")

    assert "Provider Outage" in content
    assert "Provider Outage Resolved" in content
    assert "AI Safety Handoff" in content
    assert "AI Safety Incident" in content
    assert "No unsafe autonomous reply was sent" in content
    assert "Human-review fallback" in content
