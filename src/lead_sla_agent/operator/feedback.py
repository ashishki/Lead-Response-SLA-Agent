"""Operator feedback export helpers for eval candidate generation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lead_sla_agent.observability.pii import hash_identifier

FEEDBACK_SCHEMA_VERSION = "operator-feedback-candidates-v1"
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
PHONE_PATTERN = re.compile(r"\+?\d[\d\s().-]{7,}\d")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}(?:T[\d:.]+Z)?")


@dataclass(frozen=True)
class OperatorFeedbackDecision:
    tenant_id: str
    task_id: str
    operator_action: str
    final_status: str
    reason_code: str
    original_draft: str
    final_message: str = ""
    transcript_refs: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    retrieval_target: dict[str, Any] | None = None
    tool_target: dict[str, Any] | None = None
    agent_target: dict[str, Any] | None = None
    human_approved_for_eval: bool = False
    approved_by: str | None = None
    approved_at: str | None = None


def export_feedback_candidates(
    decisions: list[OperatorFeedbackDecision],
) -> list[dict[str, Any]]:
    return [_export_decision(decision) for decision in decisions]


def load_feedback_candidates(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != FEEDBACK_SCHEMA_VERSION:
        raise ValueError("unsupported operator feedback candidate schema")
    return list(payload.get("candidates", []))


def accepted_feedback_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [candidate for candidate in candidates if is_accepted_feedback_candidate(candidate)]


def is_accepted_feedback_candidate(candidate: dict[str, Any]) -> bool:
    approval = candidate.get("approval", {})
    return (
        approval.get("status") == "accepted"
        and bool(approval.get("approved_by_hash"))
        and bool(approval.get("approved_at"))
    )


def partition_regression_targets(
    candidates: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    partitions: dict[str, list[dict[str, Any]]] = {"retrieval": [], "tool": [], "agent": []}
    for candidate in accepted_feedback_candidates(candidates):
        targets = candidate.get("eval_targets", {})
        for target_type in partitions:
            target = targets.get(target_type)
            if target is not None:
                partitions[target_type].append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        **target,
                    }
                )
    return partitions


def deidentify_text(value: str) -> str:
    value = EMAIL_PATTERN.sub("[redacted-email]", value)
    return PHONE_PATTERN.sub(_redact_phone_match, value)


def contains_direct_pii(value: str) -> bool:
    return EMAIL_PATTERN.search(value) is not None or any(
        not _is_allowed_date(match.group(0)) for match in PHONE_PATTERN.finditer(value)
    )


def _export_decision(decision: OperatorFeedbackDecision) -> dict[str, Any]:
    approval = _approval_payload(decision)
    candidate = {
        "schema_version": FEEDBACK_SCHEMA_VERSION,
        "candidate_id": _candidate_id(decision),
        "tenant_id": decision.tenant_id,
        "task_id": decision.task_id,
        "deidentified": True,
        "approval": approval,
        "operator_action": {
            "action": decision.operator_action,
            "reason_code": decision.reason_code,
            "final_status": decision.final_status,
            "original_draft_hash": _sha256(decision.original_draft),
            "final_message_hash": _sha256(decision.final_message),
        },
        "review_context": {
            "transcript_refs": decision.transcript_refs,
            "evidence_ids": decision.evidence_ids,
        },
        "eval_targets": {},
    }
    _add_target(candidate["eval_targets"], "retrieval", decision.retrieval_target)
    _add_target(candidate["eval_targets"], "tool", decision.tool_target)
    _add_target(candidate["eval_targets"], "agent", decision.agent_target)
    return candidate


def _add_target(
    targets: dict[str, Any],
    target_type: str,
    target: dict[str, Any] | None,
) -> None:
    if target is None:
        return

    targets[target_type] = _deidentify_target(target)


def _deidentify_target(target: dict[str, Any]) -> dict[str, Any]:
    deidentified: dict[str, Any] = {}
    for key, value in target.items():
        if isinstance(value, str):
            deidentified[key] = deidentify_text(value)
        elif isinstance(value, list):
            deidentified[key] = [
                deidentify_text(item) if isinstance(item, str) else item for item in value
            ]
        else:
            deidentified[key] = value
    return deidentified


def _approval_payload(decision: OperatorFeedbackDecision) -> dict[str, str | bool | None]:
    if not decision.human_approved_for_eval:
        return {
            "status": "candidate",
            "human_approved_for_eval": False,
            "approved_by_hash": None,
            "approved_at": None,
        }
    if not decision.approved_by or not decision.approved_at:
        raise ValueError("approved feedback requires approved_by and approved_at")

    return {
        "status": "accepted",
        "human_approved_for_eval": True,
        "approved_by_hash": hash_identifier(decision.approved_by),
        "approved_at": decision.approved_at,
    }


def _candidate_id(decision: OperatorFeedbackDecision) -> str:
    raw_id = ":".join(
        [
            decision.tenant_id,
            decision.task_id,
            decision.operator_action,
            decision.reason_code,
            decision.final_status,
        ]
    )
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _redact_phone_match(match: re.Match[str]) -> str:
    matched = match.group(0)
    if _is_allowed_date(matched):
        return matched
    return "[redacted-phone]"


def _is_allowed_date(value: str) -> bool:
    return DATE_PATTERN.fullmatch(value) is not None
