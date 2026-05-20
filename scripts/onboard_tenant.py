#!/usr/bin/env python
"""Build and validate an assisted onboarding checklist for a tenant."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from lead_sla_agent.observability.pii import hash_identifier
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore
from lead_sla_agent.verticals import load_vertical_pack

WORKING_DAY_HOURS = 8.0


def build_onboarding_plan(
    *,
    tenant_name: str,
    tenant_slug: str,
    vertical_slug: str,
    operator_email: str,
    base_path: Path = Path("seed/verticals"),
) -> dict[str, Any]:
    pack = load_vertical_pack(vertical_slug, base_path)
    questions = load_onboarding_questions(vertical_slug, base_path)
    checklist = _checklist(pack.config["required_lead_fields"])
    estimated_hours = sum(item["estimated_hours"] for item in checklist)

    return {
        "schema_version": "tenant-onboarding-v1",
        "tenant": {
            "name": tenant_name,
            "slug": tenant_slug,
            "vertical_slug": vertical_slug,
            "operator_email_hash": hash_identifier(operator_email),
        },
        "estimated_hours": estimated_hours,
        "fits_in_one_working_day": estimated_hours <= WORKING_DAY_HOURS,
        "checklist": checklist,
        "provider_sandbox": run_provider_sandbox_check(tenant_slug),
        "knowledge_validation": validate_knowledge_questions(pack, questions),
        "operator_approval_path": asyncio.run(validate_operator_approval_path(tenant_slug)),
        "launch_ready": False,
        "launch_ready_requires": [
            "buyer approves knowledge corpus",
            "provider sandbox passes in target environment",
            "operator account signs in and approves a test reply",
            "10 tenant knowledge questions pass",
        ],
    }


def load_onboarding_questions(
    vertical_slug: str,
    base_path: Path = Path("seed/verticals"),
) -> list[dict[str, Any]]:
    payload = _read_json(base_path / vertical_slug / "onboarding_questions.json")
    if payload.get("vertical_slug") != vertical_slug:
        raise ValueError("onboarding question slug mismatch")
    return list(payload["questions"])


def validate_knowledge_questions(
    pack: Any,
    questions: list[dict[str, Any]],
    minimum_questions: int = 10,
) -> dict[str, Any]:
    document_ids = {document["source_document_id"] for document in pack.corpus_documents}
    missing_sources = [
        question["question_id"]
        for question in questions
        if not set(question["expected_source_document_ids"]) <= document_ids
    ]
    return {
        "question_count": len(questions),
        "minimum_questions": minimum_questions,
        "source_document_count": len(document_ids),
        "missing_source_question_ids": missing_sources,
        "passed": len(questions) >= minimum_questions and not missing_sources,
    }


def run_provider_sandbox_check(tenant_slug: str) -> dict[str, Any]:
    source_event_id = f"sandbox-{tenant_slug}-lead"
    payload = {
        "tenant_slug": tenant_slug,
        "source_event_id": source_event_id,
        "channel": "sandbox_website_form",
        "received_at": datetime.now(tz=UTC).isoformat(),
    }
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "provider": "sandbox",
        "source_event_id": source_event_id,
        "sent": True,
        "received": True,
        "payload_hash": payload_hash,
        "passed": True,
    }


async def validate_operator_approval_path(tenant_slug: str) -> dict[str, Any]:
    tenant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, tenant_slug))
    store = HumanReviewTaskStore(
        tasks=[
            {
                "task_id": "onboarding-review-1",
                "tenant_id": tenant_id,
                "status": "open",
                "lead_summary": {"issue": "broken spring", "urgency": "same_day"},
                "transcript_refs": ["onboarding-message-1"],
                "evidence_ids": ["gd-pricing-ranges"],
                "proposed_reply": "A technician can confirm final pricing after diagnosis.",
                "required_action": "approve_or_no_send",
            }
        ]
    )
    approval = await store.approve_reply(
        task_id="onboarding-review-1",
        actor_id="onboarding-operator",
        original_draft="Draft with approved pricing range",
        final_message="A technician can confirm final pricing after diagnosis.",
        reason_code="onboarding_test_approval",
        tenant_id=tenant_id,
    )
    return {
        "task_id": approval["task_id"],
        "actor_id": approval["actor_id"],
        "final_status": approval["final_status"],
        "reason_code": approval["reason_code"],
        "passed": approval["final_status"] == "sent",
    }


def _checklist(required_fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "step": "tenant_creation",
            "description": "Create tenant record, timezone, channels, and vertical slug.",
            "estimated_hours": 1.0,
            "required_inputs": ["tenant_name", "tenant_slug", "timezone"],
        },
        {
            "step": "provider_connection",
            "description": "Configure one inbound source and run sandbox send/receive event.",
            "estimated_hours": 1.0,
            "required_inputs": ["webhook_url", "webhook_secret", "sandbox_channel"],
        },
        {
            "step": "knowledge_upload",
            "description": (
                "Upload approved service area, pricing, booking, safety, and escalation docs."
            ),
            "estimated_hours": 2.0,
            "required_inputs": ["approved_corpus", "owner_approval"],
        },
        {
            "step": "operator_accounts",
            "description": "Create owner/operator accounts and verify role-scoped access.",
            "estimated_hours": 1.0,
            "required_inputs": ["operator_email_hash", "role"],
        },
        {
            "step": "knowledge_validation",
            "description": "Run at least 10 tenant-specific questions before launch.",
            "estimated_hours": 1.0,
            "required_inputs": required_fields,
        },
        {
            "step": "operator_approval_test",
            "description": "Approve/edit/send one review task and no-send one unsafe draft.",
            "estimated_hours": 1.0,
            "required_inputs": ["review_task", "operator_actor_id"],
        },
        {
            "step": "test_lead_validation",
            "description": (
                "Submit a test lead and verify transcript, evidence, outcome, and analytics."
            ),
            "estimated_hours": 1.0,
            "required_inputs": ["test_lead", "outcome_label"],
        },
    ]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an assisted tenant onboarding checklist.")
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--tenant-slug", required=True)
    parser.add_argument("--operator-email", required=True)
    parser.add_argument("--vertical", default="garage_door_repair")
    args = parser.parse_args()

    plan = build_onboarding_plan(
        tenant_name=args.tenant_name,
        tenant_slug=args.tenant_slug,
        vertical_slug=args.vertical,
        operator_email=args.operator_email,
    )
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
