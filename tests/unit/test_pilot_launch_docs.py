from __future__ import annotations

from pathlib import Path


def test_launch_checklist_has_required_launch_phases_and_safety_gates() -> None:
    content = Path("docs/pilot/launch_checklist.md").read_text(encoding="utf-8")

    for section in (
        "Pilot Identity",
        "Pre-Launch Checklist",
        "Launch-Day Checklist",
        "First-Week Checklist",
        "Rollback And Fallback Checklist",
        "Buyer Signoff",
        "Launch Decision",
    ):
        assert f"## {section}" in content
    assert "Human approval is enabled for every outbound message" in content
    assert "Autonomous send remains" in content
    assert "Baseline metrics are captured before traffic is routed" in content
    assert "Buyer signs off on success criteria and stop criteria" in content


def test_launch_checklist_requires_buyer_signoff_and_fallback_plan() -> None:
    content = Path("docs/pilot/launch_checklist.md").read_text(encoding="utf-8")

    for signoff in (
        "Success criteria accepted",
        "Stop criteria accepted",
        "Baseline metrics captured",
        "Human approval required for every outbound message",
        "Rollback/fallback plan accepted",
    ):
        assert signoff in content
    assert "pause agent-initiated replies" in content
    assert "buyer resumes existing dispatch" in content
    assert "do not delete customer data" in content


def test_measurement_plan_links_launch_checklist_and_baseline_requirements() -> None:
    content = Path("docs/market/pilot_measurement_plan.md").read_text(encoding="utf-8")

    assert "docs/pilot/launch_checklist.md" in content
    assert "Baseline metrics must be captured before launch" in content
    assert "Human approval remains required for every outbound message at launch" in content
    assert "Stop criteria must be accepted before launch" in content


def test_runbook_links_first_pilot_launch_checklist() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "## First Pilot Launch" in content
    assert "docs/pilot/launch_checklist.md" in content
    assert "human approval required for every outbound message at launch" in content
    assert "baseline metrics captured before traffic is routed" in content
    assert "fallback path can pause agent replies" in content
