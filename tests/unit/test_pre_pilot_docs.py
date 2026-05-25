from __future__ import annotations

from pathlib import Path

PRE_PILOT_DOCS = [
    Path("docs/market/pre_pilot_evidence_plan.md"),
    Path("docs/market/pre_pilot_evidence_report.md"),
    Path("docs/market/pre_pilot_demo_script.md"),
    Path("docs/market/expert_review_rubric.md"),
    Path("docs/market/baseline_comparison.md"),
    Path("docs/market/failure_mode_replay.md"),
]


def test_pre_pilot_docs_exist_and_state_claim_boundaries() -> None:
    for path in PRE_PILOT_DOCS:
        content = path.read_text(encoding="utf-8")

        assert "pre-pilot" in content.lower()
        assert "production ROI" in content
        assert "autonomous-send" in content
        assert "paid production readiness" in content


def test_pre_pilot_evidence_report_has_buyer_ready_artifact_map() -> None:
    content = Path("docs/market/pre_pilot_evidence_report.md").read_text(encoding="utf-8")

    for artifact in (
        "garage_door_leads.json",
        "pre_pilot_replay_report.json",
        "baseline_comparison_report.json",
        "failure_mode_replay_report.json",
        "expert_review_rubric.md",
        "pre_pilot_demo_script.md",
    ):
        assert artifact in content
    assert "50 synthetic controlled scenarios" in content
    assert "21 scenario categories" in content
    assert "0 autonomous sends" in content
    assert "0 unsafe autonomous sends" in content
    assert "We do not have live production proof yet" in content
    assert "Real Pilot Proof Still Needed" in content


def test_pre_pilot_docs_do_not_make_unsupported_positive_claims() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in PRE_PILOT_DOCS)
    forbidden_positive_claims = (
        "we have live production proof",
        "production roi is proven by live clients",
        "conversion lift is proven by live clients",
        "autonomous-send safety is proven by live clients",
        "ready for paid production rollout",
    )

    lowered = combined.lower()
    for forbidden in forbidden_positive_claims:
        assert forbidden not in lowered


def test_expert_review_rubric_supports_external_validation_without_pii() -> None:
    content = Path("docs/market/expert_review_rubric.md").read_text(encoding="utf-8")

    for rating in ("would_send", "needs_edit", "escalate", "unsafe_or_wrong"):
        assert rating in content
    for field in (
        "scenario_id",
        "correction_summary",
        "missed_urgency",
        "should_have_escalated",
        "reviewer_role",
    ):
        assert field in content
    assert "Do not collect raw customer names" in content
    assert "Every `unsafe_or_wrong` case becomes a regression fixture" in content


def test_pre_pilot_demo_script_has_shadow_mode_and_expert_review_asks() -> None:
    content = Path("docs/market/pre_pilot_demo_script.md").read_text(encoding="utf-8")

    assert "shadow-mode pilot" in content
    assert "human approval" in content
    assert "review 30 controlled examples" in content
    assert "No autonomous-send customer-facing sends" in content
    assert "No production ROI claim" in content
