from __future__ import annotations

import re
from pathlib import Path


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
    assert "at least 5 of these 10 accounts confirm urgent lead-response pain" in content


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


def test_objection_doc_covers_required_sales_risks() -> None:
    content = Path("docs/market/objections.md").read_text(encoding="utf-8")

    for objection in ("Safety", "Data", "Integration", "Pricing"):
        assert f"## {objection}" in content
    assert "Attribution" in content
    assert "answering service" in content
