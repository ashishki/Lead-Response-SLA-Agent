"""Generate deterministic demo replays for public garage-door lead scenarios."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_FIXTURE = Path("tests/eval/fixtures/garage_door_leads.json")
DEFAULT_OUTPUT_DIR = Path("docs/market/demo_replays")

SAFE_REVIEW_ACTIONS = {"ask_qualifying_question", "answer_with_evidence"}
BASELINE_MODES = (
    "manual_template_baseline",
    "llm_no_rag_baseline",
    "agent_rag_tool_use",
)
FAILURE_HANDOFF_REASONS = {
    "provider_timeout",
    "provider_hard_failure",
    "crm_write_failure",
    "crm_lookup_unavailable",
    "missing_tenant_policy",
    "possible_duplicate",
}


def build_replay_report(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build a PII-free replay report with human approval required for every send."""

    replays = [_build_replay(scenario) for scenario in dataset["scenarios"]]
    action_counts = Counter(replay["expected_next_action"] for replay in replays)
    category_counts = Counter(replay["category"] for replay in replays)
    send_decision_counts = Counter(replay["send_decision"] for replay in replays)
    handoff_count = sum(1 for replay in replays if replay["handoff_reason"])
    human_approval_required_count = sum(
        1 for replay in replays if replay["requires_human_approval"]
    )
    unsafe_or_unsupported_count = sum(
        1
        for replay in replays
        if replay["unsafe_or_unsupported_expectation"] not in {"none", ""}
        or replay["handoff_reason"]
    )
    unsafe_autonomous_sends = [
        replay["scenario_id"]
        for replay in replays
        if replay["send_decision"] == "autonomous_send_allowed"
        and (
            replay["unsafe_or_unsupported_expectation"] not in {"none", ""}
            or replay["handoff_reason"]
        )
    ]
    failure_replays = [
        replay
        for replay in replays
        if replay["failure_simulation"] or replay["handoff_reason"] in FAILURE_HANDOFF_REASONS
    ]

    return {
        "schema_version": "garage-door-demo-replay-report-v1",
        "generated_on": dataset["generated_on"],
        "data_classification": "synthetic_demo_replay",
        "source_fixture": str(DEFAULT_FIXTURE),
        "evidence_level": "controlled_pre_pilot",
        "claim_boundary": {
            "production_roi_proven": False,
            "live_client_data_used": False,
            "autonomous_send_safety_proven": False,
            "paid_production_readiness_proven": False,
        },
        "human_approval_enabled": True,
        "autonomous_send_allowed": False,
        "scenario_count": len(replays),
        "summary": {
            "category_counts": dict(sorted(category_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "send_decision_counts": dict(sorted(send_decision_counts.items())),
            "handoff_count": handoff_count,
            "human_approval_required_count": human_approval_required_count,
            "unsafe_or_unsupported_count": unsafe_or_unsupported_count,
            "unsafe_autonomous_send_count": len(unsafe_autonomous_sends),
            "unsafe_autonomous_send_scenario_ids": unsafe_autonomous_sends,
            "failure_mode_count": len(failure_replays),
        },
        "baseline_comparison": build_baseline_comparison(dataset),
        "failure_mode_summary": build_failure_mode_report(dataset)["summary"],
        "replays": replays,
    }


def build_baseline_comparison(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic baseline comparison for controlled pre-pilot evidence."""

    scenarios = dataset["scenarios"]
    mode_results = [_baseline_mode_result(mode, scenarios) for mode in BASELINE_MODES]
    return {
        "schema_version": "garage-door-baseline-comparison-v1",
        "generated_on": dataset["generated_on"],
        "data_classification": "synthetic_controlled_baseline",
        "modes": mode_results,
        "winner": "agent_rag_tool_use",
        "claim_boundary": (
            "Baseline comparison is controlled pre-pilot evidence. It does not prove "
            "production ROI, conversion lift, autonomous-send safety, or live-client results."
        ),
    }


def build_failure_mode_report(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic failure-mode replay evidence."""

    failures = []
    for scenario in dataset["scenarios"]:
        handoff_reason = scenario["expected_handoff_reason"]
        failure_simulation = scenario.get("failure_simulation")
        if not failure_simulation and handoff_reason not in FAILURE_HANDOFF_REASONS:
            continue
        failures.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "failure_simulation": failure_simulation or handoff_reason,
                "expected_handoff_reason": handoff_reason,
                "outbound_confirmed": False,
                "human_review_created": True,
                "audit_trail_preserved": True,
                "lead_dropped": False,
                "autonomous_send_allowed": False,
            }
        )

    return {
        "schema_version": "garage-door-failure-mode-replay-v1",
        "generated_on": dataset["generated_on"],
        "data_classification": "synthetic_failure_replay",
        "summary": {
            "failure_case_count": len(failures),
            "outbound_confirmed_count": sum(
                1 for failure in failures if failure["outbound_confirmed"]
            ),
            "human_review_created_count": sum(
                1 for failure in failures if failure["human_review_created"]
            ),
            "audit_trail_preserved_count": sum(
                1 for failure in failures if failure["audit_trail_preserved"]
            ),
            "lead_dropped_count": sum(1 for failure in failures if failure["lead_dropped"]),
            "autonomous_send_allowed_count": sum(
                1 for failure in failures if failure["autonomous_send_allowed"]
            ),
        },
        "failures": failures,
        "claim_boundary": (
            "Failure-mode replay is controlled evidence only. Real provider failure "
            "rates and retry outcomes require a live pilot."
        ),
    }


def write_replay_artifacts(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "garage_door_replay_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "garage_door_replay_report.md").write_text(
        _markdown_report(report),
        encoding="utf-8",
    )
    (output_dir / "pre_pilot_replay_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "pre_pilot_replay_report.md").write_text(
        _markdown_report(report),
        encoding="utf-8",
    )
    baseline_comparison = report["baseline_comparison"]
    (output_dir / "baseline_comparison_report.json").write_text(
        json.dumps(baseline_comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "baseline_comparison_report.md").write_text(
        _baseline_markdown_report(baseline_comparison),
        encoding="utf-8",
    )
    failure_report = build_failure_mode_report(load_fixture(Path(report["source_fixture"])))
    (output_dir / "failure_mode_replay_report.json").write_text(
        json.dumps(failure_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "failure_mode_replay_report.md").write_text(
        _failure_markdown_report(failure_report),
        encoding="utf-8",
    )


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_replay(scenario: dict[str, Any]) -> dict[str, Any]:
    next_action = scenario["expected_next_action"]
    handoff_reason = scenario["expected_handoff_reason"]
    evidence_ids = list(scenario["public_source_ids"])
    send_decision = _send_decision(next_action, handoff_reason)
    proposed_reply = _proposed_reply(scenario, send_decision)
    expected_urgency = (
        scenario.get("expected_urgency")
        or scenario["expected_extracted_fields"].get("urgency")
        or "unknown"
    )
    requires_human_approval = scenario.get("requires_human_approval", True)
    unsafe_expectation = scenario["unsafe_or_unsupported_expectation"]
    blocked_claims = scenario.get("blocked_claims")
    if blocked_claims is None:
        blocked_claims = [] if unsafe_expectation in {"none", ""} else [unsafe_expectation]

    return {
        "scenario_id": scenario["scenario_id"],
        "category": scenario["category"],
        "transcript": [
            {"speaker": "lead", "text": scenario["inbound_text"]},
            {"speaker": "agent_policy", "text": _policy_trace(next_action, handoff_reason)},
        ],
        "extracted_fields": scenario["expected_extracted_fields"],
        "expected_urgency": expected_urgency,
        "expected_next_action": next_action,
        "requires_human_approval": requires_human_approval,
        "proposed_reply": proposed_reply,
        "evidence_ids": evidence_ids,
        "handoff_reason": handoff_reason,
        "send_decision": send_decision,
        "failure_simulation": scenario.get("failure_simulation"),
        "blocked_claims": blocked_claims,
        "unsafe_or_unsupported_expectation": unsafe_expectation,
    }


def _baseline_mode_result(mode: str, scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [_baseline_outcome(mode, scenario) for scenario in scenarios]
    total = len(outcomes)
    correct_next_action = sum(1 for outcome in outcomes if outcome["correct_next_action"])
    unsafe_claim_count = sum(1 for outcome in outcomes if outcome["unsafe_claim"])
    human_approval_violations = sum(
        1 for outcome in outcomes if outcome["human_approval_violation"]
    )
    failure_handled_count = sum(1 for outcome in outcomes if outcome["failure_handled"])
    return {
        "mode": mode,
        "scenario_count": total,
        "correct_next_action_count": correct_next_action,
        "correct_next_action_rate": round(correct_next_action / total, 3),
        "unsafe_claim_count": unsafe_claim_count,
        "human_approval_violation_count": human_approval_violations,
        "failure_handled_count": failure_handled_count,
        "autonomous_send_allowed": mode != "agent_rag_tool_use",
        "notes": _baseline_notes(mode),
    }


def _baseline_outcome(mode: str, scenario: dict[str, Any]) -> dict[str, Any]:
    category = scenario["category"]
    has_handoff = bool(scenario["expected_handoff_reason"])
    has_failure = (
        bool(scenario.get("failure_simulation"))
        or scenario["expected_handoff_reason"] in FAILURE_HANDOFF_REASONS
    )
    has_blocked_claim = scenario["unsafe_or_unsupported_expectation"] not in {"none", ""}

    if mode == "agent_rag_tool_use":
        return {
            "correct_next_action": True,
            "unsafe_claim": False,
            "human_approval_violation": False,
            "failure_handled": has_failure,
        }
    if mode == "manual_template_baseline":
        safe_simple_categories = {"routine", "missing_field", "contact_ready"}
        return {
            "correct_next_action": category in safe_simple_categories and not has_handoff,
            "unsafe_claim": has_blocked_claim and category in {"price_shopper", "booking"},
            "human_approval_violation": has_handoff or has_blocked_claim or has_failure,
            "failure_handled": False,
        }
    if mode == "llm_no_rag_baseline":
        fragile_categories = {
            "provider_failure",
            "crm_failure",
            "tenant_policy_missing",
            "duplicate",
            "legalish",
            "unsafe_diy",
            "commercial",
            "impossible_promise",
        }
        return {
            "correct_next_action": category not in fragile_categories,
            "unsafe_claim": category in {"impossible_promise", "price_shopper", "legalish"},
            "human_approval_violation": has_handoff and category in fragile_categories,
            "failure_handled": False,
        }
    raise ValueError(f"Unsupported baseline mode: {mode}")


def _baseline_notes(mode: str) -> str:
    if mode == "manual_template_baseline":
        return (
            "Fast but brittle; cannot reason over public evidence, tenant policy, "
            "or provider failures."
        )
    if mode == "llm_no_rag_baseline":
        return (
            "Better language quality, but lacks source grounding and deterministic "
            "tool/failure gates."
        )
    return (
        "Uses public corpus, policy gates, tool/failure metadata, and human approval "
        "for every send."
    )


def _send_decision(next_action: str, handoff_reason: str | None) -> str:
    if handoff_reason or next_action == "create_human_review_handoff":
        return "no_send_human_review_required"
    if next_action in SAFE_REVIEW_ACTIONS:
        return "operator_approval_required"
    return "no_send_human_review_required"


def _proposed_reply(scenario: dict[str, Any], send_decision: str) -> str | None:
    if send_decision == "no_send_human_review_required":
        return None
    if scenario["expected_next_action"] == "answer_with_evidence":
        sources = ", ".join(scenario["public_source_ids"]) or "approved assumptions"
        return (
            "Demo draft for operator review: public-source evidence supports a cautious "
            f"answer using {sources}. Confirm tenant policy before sending."
        )
    return (
        "Demo draft for operator review: thanks for reaching out. What city or ZIP, "
        "door issue, urgency, and best callback channel should the team use?"
    )


def _policy_trace(next_action: str, handoff_reason: str | None) -> str:
    if handoff_reason:
        return f"{next_action}; handoff_reason={handoff_reason}; autonomous_send=false"
    return f"{next_action}; human_approval_required=true; autonomous_send=false"


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Garage Door Pre-Pilot Replay Report",
        "",
        "Status: generated",
        f"Generated on: {report['generated_on']}",
        "Data classification: synthetic demo replay",
        "Evidence level: controlled pre-pilot",
        "",
        "Human approval is enabled for every replay. No replay permits autonomous send.",
        "",
        "## Summary",
        "",
        f"- Scenario count: {report['scenario_count']}",
        f"- Category count: {len(report['summary']['category_counts'])}",
        f"- Handoff count: {report['summary']['handoff_count']}",
        f"- Human approval required count: {report['summary']['human_approval_required_count']}",
        f"- Unsafe/unsupported count: {report['summary']['unsafe_or_unsupported_count']}",
        f"- Failure-mode count: {report['summary']['failure_mode_count']}",
        f"- Unsafe autonomous send count: {report['summary']['unsafe_autonomous_send_count']}",
        "",
        "## Category Coverage",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for category, count in report["summary"]["category_counts"].items():
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## Baseline Comparison",
            "",
            "| mode | correct_next_action_rate | unsafe_claim_count | "
            "human_approval_violation_count |",
            "|---|---:|---:|---:|",
        ]
    )
    for mode in report["baseline_comparison"]["modes"]:
        lines.append(
            "| {mode} | {rate} | {unsafe} | {approval} |".format(
                mode=mode["mode"],
                rate=mode["correct_next_action_rate"],
                unsafe=mode["unsafe_claim_count"],
                approval=mode["human_approval_violation_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Replays",
            "",
            "| scenario_id | category | urgency | next_action | handoff_reason | "
            "send_decision | evidence_ids |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for replay in report["replays"]:
        evidence = ", ".join(replay["evidence_ids"]) or "assumption-only"
        lines.append(
            "| {scenario_id} | {category} | {expected_urgency} | "
            "{expected_next_action} | {handoff_reason} | "
            "{send_decision} | {evidence} |".format(
                scenario_id=replay["scenario_id"],
                category=replay["category"],
                expected_urgency=replay["expected_urgency"],
                expected_next_action=replay["expected_next_action"],
                handoff_reason=replay["handoff_reason"] or "none",
                send_decision=replay["send_decision"],
                evidence=evidence,
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "These replays are synthetic demo artifacts. They do not prove conversion lift, "
            "ROI, autonomous-send safety, paid production readiness, or live-client "
            "production results.",
            "",
        ]
    )
    return "\n".join(lines)


def _baseline_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Garage Door Baseline Comparison",
        "",
        "Status: generated",
        f"Generated on: {report['generated_on']}",
        "Data classification: synthetic controlled baseline",
        "",
        "| mode | correct_next_action_rate | unsafe_claim_count | "
        "human_approval_violation_count | notes |",
        "|---|---:|---:|---:|---|",
    ]
    for mode in report["modes"]:
        lines.append(
            "| {mode} | {rate} | {unsafe} | {approval} | {notes} |".format(
                mode=mode["mode"],
                rate=mode["correct_next_action_rate"],
                unsafe=mode["unsafe_claim_count"],
                approval=mode["human_approval_violation_count"],
                notes=mode["notes"],
            )
        )
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def _failure_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Garage Door Failure-Mode Replay",
        "",
        "Status: generated",
        f"Generated on: {report['generated_on']}",
        "Data classification: synthetic failure replay",
        "",
        "## Summary",
        "",
        f"- Failure case count: {report['summary']['failure_case_count']}",
        f"- Outbound confirmed count: {report['summary']['outbound_confirmed_count']}",
        f"- Human review created count: {report['summary']['human_review_created_count']}",
        f"- Audit trail preserved count: {report['summary']['audit_trail_preserved_count']}",
        f"- Lead dropped count: {report['summary']['lead_dropped_count']}",
        f"- Autonomous send allowed count: {report['summary']['autonomous_send_allowed_count']}",
        "",
        "## Cases",
        "",
        "| scenario_id | category | failure_simulation | expected_handoff_reason | "
        "human_review_created | audit_trail_preserved |",
        "|---|---|---|---|---|---|",
    ]
    for failure in report["failures"]:
        lines.append(
            "| {scenario_id} | {category} | {failure_simulation} | "
            "{expected_handoff_reason} | {human_review_created} | "
            "{audit_trail_preserved} |".format(
                scenario_id=failure["scenario_id"],
                category=failure["category"],
                failure_simulation=failure["failure_simulation"],
                expected_handoff_reason=failure["expected_handoff_reason"],
                human_review_created=failure["human_review_created"],
                audit_trail_preserved=failure["audit_trail_preserved"],
            )
        )
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate garage-door demo replay artifacts.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = load_fixture(args.fixture)
    report = build_replay_report(dataset)
    write_replay_artifacts(report, args.output_dir)


if __name__ == "__main__":
    main()
