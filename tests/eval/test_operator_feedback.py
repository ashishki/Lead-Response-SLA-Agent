from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lead_sla_agent.operator.feedback import (
    OperatorFeedbackDecision,
    accepted_feedback_candidates,
    contains_direct_pii,
    export_feedback_candidates,
    load_feedback_candidates,
    partition_regression_targets,
)

FIXTURE = Path("tests/eval/fixtures/operator_feedback_candidates.json")


def test_feedback_export_deidentifies_operator_decisions() -> None:
    candidates = export_feedback_candidates(
        [
            OperatorFeedbackDecision(
                tenant_id="tenant-1",
                task_id="review-1",
                operator_action="approve_with_edit",
                final_status="sent",
                reason_code="operator_edit",
                original_draft="Email sam@example.com or call +1 555 010 9999",
                final_message="We can help with the service request.",
                transcript_refs=["message-1"],
                evidence_ids=["faq-1"],
                retrieval_target={
                    "query": "Can sam@example.com get service at +1 555 010 9999?",
                    "expected_status": "evidence",
                    "expected_source_document_ids": ["faq-1"],
                },
                human_approved_for_eval=True,
                approved_by="operator-1",
                approved_at="2026-05-20T12:00:00Z",
            )
        ]
    )

    serialized = json.dumps(candidates)
    candidate = candidates[0]

    assert "sam@example.com" not in serialized
    assert "+1 555 010 9999" not in serialized
    assert candidate["operator_action"]["original_draft_hash"]
    assert candidate["operator_action"]["final_message_hash"]
    assert candidate["approval"]["approved_by_hash"].startswith("sha256:")
    assert candidate["eval_targets"]["retrieval"]["query"] == (
        "Can [redacted-email] get service at [redacted-phone]?"
    )


def test_unapproved_feedback_is_excluded_from_canonical_eval_sets() -> None:
    candidates = export_feedback_candidates(
        [
            OperatorFeedbackDecision(
                tenant_id="tenant-1",
                task_id="review-approved",
                operator_action="no_send",
                final_status="no_send",
                reason_code="unsafe_or_wrong",
                original_draft="Do not send",
                human_approved_for_eval=True,
                approved_by="operator-1",
                approved_at="2026-05-20T12:00:00Z",
                agent_target={"scenario": "unsafe", "expected_termination_reason": "human_review"},
            ),
            OperatorFeedbackDecision(
                tenant_id="tenant-1",
                task_id="review-candidate",
                operator_action="approve_with_edit",
                final_status="sent",
                reason_code="needs_review",
                original_draft="Still pending approval",
                retrieval_target={"query": "Pending case", "expected_status": "evidence"},
            ),
        ]
    )

    accepted = accepted_feedback_candidates(candidates)
    partitions = partition_regression_targets(candidates)

    assert [candidate["task_id"] for candidate in accepted] == ["review-approved"]
    assert partitions["agent"][0]["candidate_id"] == accepted[0]["candidate_id"]
    assert partitions["retrieval"] == []


def test_operator_feedback_fixture_contains_no_direct_pii() -> None:
    candidates = load_feedback_candidates(FIXTURE)
    text_payload = json.dumps(
        [
            {
                "review_context": candidate["review_context"],
                "eval_targets": candidate["eval_targets"],
            }
            for candidate in candidates
        ]
    )

    assert not re.search(
        r"\b[\w.+-]+@[\w.-]+\.\w+\b",
        text_payload,
    )
    assert all(candidate["deidentified"] is True for candidate in candidates)
    assert not contains_direct_pii(text_payload)


def test_accepted_feedback_fixture_runs_regression_partitions() -> None:
    candidates = load_feedback_candidates(FIXTURE)
    partitions = partition_regression_targets(candidates)

    assert len(accepted_feedback_candidates(candidates)) == 3
    assert partitions["retrieval"] == [
        {
            "candidate_id": "opfb-retrieval-001",
            "slice": "operator_feedback",
            "query": "Do you cover the north route on Saturday morning?",
            "expected_status": "evidence",
            "expected_source_document_ids": ["service-area-policy"],
        }
    ]
    assert partitions["tool"][0]["tool_name"] == "book_slot"
    assert partitions["tool"][0]["expected_result"] == "human_review_required"
    assert partitions["agent"][0]["expected_termination_reason"] == "unsupported_question"


def test_approved_feedback_requires_reviewer_metadata() -> None:
    with pytest.raises(ValueError, match="approved feedback requires approved_by and approved_at"):
        export_feedback_candidates(
            [
                OperatorFeedbackDecision(
                    tenant_id="tenant-1",
                    task_id="review-invalid",
                    operator_action="no_send",
                    final_status="no_send",
                    reason_code="unsafe_or_wrong",
                    original_draft="Missing reviewer metadata",
                    human_approved_for_eval=True,
                )
            ]
        )
