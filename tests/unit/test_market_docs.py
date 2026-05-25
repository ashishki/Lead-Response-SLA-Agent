from __future__ import annotations

import re
from pathlib import Path

SOURCE_REGISTER = Path("docs/market/public_corpus/garage_door_repair_source_register.md")


def test_pilot_vertical_doc_selects_one_vertical_and_metrics() -> None:
    content = Path("docs/market/pilot_vertical.md").read_text(encoding="utf-8")

    assert "DFW Emergency Garage Door Repair" in content
    assert "Rejected Alternatives" in content
    assert "Buyer Persona" in content
    assert "Current workaround" in content
    for metric in (
        "Median first response time",
        "Missed lead rate",
        "Booking rate",
        "Manual review cost",
    ):
        assert metric in content
    assert "Invoca" in content
    assert "Forbes" in content
    assert "Angi" in content


def test_first_10_targets_doc_has_ten_accounts_and_validation_gate() -> None:
    content = Path("docs/market/first_10_targets.md").read_text(encoding="utf-8")
    target_rows = re.findall(r"^\| \d+ \|", content, flags=re.MULTILINE)

    assert len(target_rows) == 10
    assert "Primary channel" in content
    assert "Secondary channel" in content
    assert "docs/market/demo_report_garage_door_repair.md" in content
    assert "No automated outreach is executed by the product or agent" in content
    assert "narrow replay/pilot conversation" in content
    assert "at least 5 of these 10 accounts" in content
    for source_id in ("GD-PUB-001", "GD-PUB-010", "GD-PUB-019", "GD-PUB-029"):
        assert source_id in content


def test_pilot_measurement_plan_defines_periods_and_metrics() -> None:
    content = Path("docs/market/pilot_measurement_plan.md").read_text(encoding="utf-8")

    assert "Baseline period" in content
    assert "Pilot period" in content
    for metric in (
        "Response time p50/p95",
        "Lead capture rate",
        "Booked calls/jobs",
        "Qualified handoffs",
        "Human-review rate",
        "Cost per lead handled",
    ):
        assert metric in content
    assert "Buyer agrees that payment/expansion decision will use this metric set" in content


def test_weekly_report_template_has_buyer_update_sections() -> None:
    content = Path("docs/market/weekly_report_template.md").read_text(encoding="utf-8")

    for section in (
        "Executive Summary",
        "Scorecard",
        "Revenue And Labor Impact",
        "Safety And Quality",
        "Buyer Decision",
    ):
        assert section in content
    assert "Cost per lead handled" in content
    assert "Do not include customer names" in content


def test_pricing_doc_has_value_aligned_hypotheses_and_decision_log() -> None:
    content = Path("docs/market/pricing.md").read_text(encoding="utf-8")

    assert "Price Hypotheses" in content
    assert "Recovery Pilot" in content
    assert "Booked-Lead Share" in content
    assert "Dispatcher Assist" in content
    assert "Review Workload Adjustment" in content
    assert "Pricing Decision Log" in content
    assert "recovered booked jobs" in content


def test_pilot_terms_define_contract_shape_and_success_criteria() -> None:
    content = Path("docs/market/pilot_terms.md").read_text(encoding="utf-8")

    for section in (
        "Pilot Offer",
        "Commercial Terms To Test",
        "Buyer Responsibilities",
        "Provider Responsibilities",
        "Success Criteria",
        "Stop Criteria",
        "Objections To Capture",
    ):
        assert section in content
    assert "at least 3 incremental booked jobs" in content
    assert "human-review rate remains above 50 percent" in content


def test_case_study_template_contains_required_proof_sections() -> None:
    content = Path("docs/market/case_study_template.md").read_text(encoding="utf-8")

    for section in (
        "Baseline",
        "Intervention",
        "Measurable Result",
        "Operator Feedback",
        "Buyer Quote Slot",
    ):
        assert section in content
    assert "Unsafe autonomous replies" in content
    assert "Do not include raw customer names" in content


def test_demo_script_maps_to_garage_door_pain() -> None:
    content = Path("docs/market/demo_script.md").read_text(encoding="utf-8")

    assert "garage door repair owner/operator" in content
    assert "same-day or emergency garage door repair" in content
    assert "exact spring replacement price" in content
    assert "booking blocked until explicit acceptance" in content
    assert "recovered jobs and dispatcher burden" in content


def test_public_research_protocol_defines_sources_register_and_claim_limits() -> None:
    content = Path("docs/market/open_source_research_protocol.md").read_text(encoding="utf-8")

    for section in (
        "Allowed Sources",
        "Forbidden Sources",
        "Required Source Register",
        "Claim Rule",
        "Demo Artifact Rules",
    ):
        assert f"## {section}" in content
    for field in (
        "source_url_or_locator",
        "captured_at",
        "company_or_source_type",
        "evidence_kind",
        "extracted_fact",
        "demo_use",
        "limitation",
        "pii_contact_handling",
    ):
        assert field in content
    for blocked_claim in (
        "conversion lift",
        "ROI",
        "autonomous-send safety",
        "paid production readiness",
    ):
        assert blocked_claim in content


def test_market_docs_link_public_research_protocol_for_demo_pack_work() -> None:
    protocol_path = "docs/market/open_source_research_protocol.md"
    pilot_vertical = Path("docs/market/pilot_vertical.md").read_text(encoding="utf-8")
    demo_script = Path("docs/market/demo_script.md").read_text(encoding="utf-8")

    assert protocol_path in pilot_vertical
    assert protocol_path in demo_script
    assert "synthetic demo" in pilot_vertical
    assert "synthetic demo" in demo_script
    for blocked_claim in (
        "conversion lift",
        "ROI",
        "autonomous-send safety",
        "paid production readiness",
    ):
        assert blocked_claim in pilot_vertical
        assert blocked_claim in demo_script


def test_garage_door_public_source_register_has_required_records() -> None:
    content = SOURCE_REGISTER.read_text(encoding="utf-8")
    rows = re.findall(r"^\| GD-PUB-\d{3} \|", content, flags=re.MULTILINE)

    assert len(rows) >= 30
    for header in (
        "source_url_or_locator",
        "captured_at",
        "company_or_source_type",
        "evidence_kind",
        "extracted_fact",
        "demo_use",
        "limitation",
        "pii_contact_handling",
    ):
        assert header in content
    for evidence_kind in (
        "service_area",
        "pricing_range",
        "booking_rule",
        "emergency_claim",
        "repair_taxonomy",
        "commercial_note",
        "safety",
    ):
        assert evidence_kind in content
    assert "conversion lift, ROI, autonomous-send safety, or paid" in content
    assert "private lead logs" in content
    assert "Public business page only; no customer PII copied." in content


def test_garage_door_public_seed_corpus_links_source_register() -> None:
    content = Path("seed/verticals/garage_door_repair/public_corpus.json").read_text(
        encoding="utf-8"
    )

    assert "public-vertical-corpus-v1" in content
    assert str(SOURCE_REGISTER) in content
    for category in (
        "service_area",
        "emergency_claim",
        "repair_taxonomy",
        "pricing_range",
        "booking_rule",
        "safety",
        "commercial_note",
    ):
        assert f'"category": "{category}"' in content
    for blocked_claim in (
        "conversion lift",
        "ROI",
        "autonomous-send safety",
        "paid production readiness",
    ):
        assert blocked_claim in content


def test_garage_door_demo_report_packages_public_showcase_without_claims() -> None:
    content = Path("docs/market/demo_report_garage_door_repair.md").read_text(encoding="utf-8")

    for section in (
        "Artifact Map",
        "Vertical Corpus Summary",
        "Scenario Coverage",
        "Replay Metrics",
        "Demo Examples",
        "Safety Boundaries",
        "Missing Real-Pilot Evidence",
        "Real Pilot Proof Plan",
    ):
        assert f"## {section}" in content
    for artifact in (
        "garage_door_repair_source_register.md",
        "garage_door_leads.json",
        "garage_door_replay_report.json",
    ):
        assert artifact in content
    assert "35 public source records" in content
    assert "50 synthetic" in content
    assert "Unsafe autonomous send count | 0" in content
    for blocked_claim in (
        "conversion lift",
        "ROI",
        "autonomous-send safety",
        "paid production readiness",
    ):
        assert blocked_claim in content
    assert "Required proof" in content


def test_demo_script_links_report_and_real_pilot_proof_ask() -> None:
    content = Path("docs/market/demo_script.md").read_text(encoding="utf-8")

    assert "docs/market/demo_report_garage_door_repair.md" in content
    assert "35 public source records" in content
    assert "50 synthetic lead" in content
    assert "zero unsafe autonomous sends" in content
    assert "Real Pilot Proof Ask" in content
    assert "booked-job attribution" in content
    assert "docs/market/first_10_targets.md" in content
    assert "Outreach is manual" in content
    assert "no automated email" in content


def test_pilot_terms_keep_public_showcase_out_of_paid_terms() -> None:
    content = Path("docs/market/pilot_terms.md").read_text(encoding="utf-8")

    assert "Pre-pilot note" in content
    assert "manual replay/pilot conversation" in content
    assert "Before accepting real lead data or payment" in content
    for blocked_claim in (
        "conversion lift",
        "ROI",
        "autonomous-send safety",
        "paid production readiness",
    ):
        assert blocked_claim in content


def test_solo_showcase_readiness_review_records_decision_and_no_go_conditions() -> None:
    content = Path("docs/audit/SOLO_SHOWCASE_READINESS_REVIEW.md").read_text(encoding="utf-8")

    assert "SOLO_SHOWCASE_READINESS_REVIEW: PASS" in content
    for artifact in (
        "garage_door_repair_source_register.md",
        "garage_door_leads.json",
        "garage_door_replay_report.json",
        "demo_report_garage_door_repair.md",
        "first_10_targets.md",
    ):
        assert artifact in content
    assert "No-Go Conditions" in content
    assert "Missing Real-Pilot Evidence" in content
    assert "founder-led manual outreach" in content
    assert "Codex should not resume T64 until the human approves" in content


def test_objection_doc_covers_required_sales_risks() -> None:
    content = Path("docs/market/objections.md").read_text(encoding="utf-8")

    for objection in ("Safety", "Data", "Integration", "Pricing"):
        assert f"## {objection}" in content
    assert "Attribution" in content
    assert "answering service" in content
