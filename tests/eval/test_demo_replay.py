from __future__ import annotations

import json
from pathlib import Path

from scripts.replay_demo_leads import build_replay_report

FIXTURE = Path("tests/eval/fixtures/garage_door_leads.json")
REPORT_JSON = Path("docs/market/demo_replays/garage_door_replay_report.json")
REPORT_MD = Path("docs/market/demo_replays/garage_door_replay_report.md")


def test_demo_replay_report_matches_fixture_and_required_fields() -> None:
    dataset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = build_replay_report(dataset)

    assert report["human_approval_enabled"] is True
    assert report["autonomous_send_allowed"] is False
    assert report["scenario_count"] == len(dataset["scenarios"]) >= 30
    for replay in report["replays"]:
        assert replay["transcript"]
        assert replay["extracted_fields"]
        assert "proposed_reply" in replay
        assert "evidence_ids" in replay
        assert "handoff_reason" in replay
        assert "send_decision" in replay


def test_demo_replay_blocks_unsafe_unsupported_and_low_confidence_autosends() -> None:
    dataset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = build_replay_report(dataset)

    assert report["summary"]["unsafe_autonomous_send_count"] == 0
    for replay in report["replays"]:
        if replay["handoff_reason"] or replay["unsafe_or_unsupported_expectation"] not in {
            "none",
            "",
        }:
            assert replay["send_decision"] != "autonomous_send_allowed"
        else:
            assert replay["send_decision"] == "operator_approval_required"


def test_committed_demo_replay_artifacts_are_reproducible() -> None:
    dataset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected_report = build_replay_report(dataset)
    committed_report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    markdown = REPORT_MD.read_text(encoding="utf-8")

    assert committed_report == expected_report
    assert "Human approval is enabled for every replay" in markdown
    assert "Unsafe autonomous send count: 0" in markdown
    for replay in expected_report["replays"]:
        assert replay["scenario_id"] in markdown
