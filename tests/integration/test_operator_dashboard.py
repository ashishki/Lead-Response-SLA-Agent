from __future__ import annotations

import hashlib

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.operator.auth import OPERATOR_TEST_TOKEN
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

AUTH_HEADERS = {"authorization": f"Bearer {OPERATOR_TEST_TOKEN}"}


@pytest.mark.asyncio
async def test_operator_console_lists_review_context() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {
                "task_id": "review-1",
                "tenant_id": "tenant-1",
                "lead_summary": {
                    "lead_id": "lead-1",
                    "status": "qualified",
                    "service": "garage door repair",
                },
                "handoff_reason": "unsupported_question",
                "transcript_refs": ["message-1", "message-2"],
                "evidence_ids": ["faq-1", "policy-2"],
                "proposed_reply": "I can check that policy with the office.",
                "required_action": "approve_or_no_send",
                "status": "open",
            }
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/operator/reviews", headers=AUTH_HEADERS)

    assert response.status_code == 200
    task = response.json()["tasks"][0]
    assert task["lead_summary"] == {
        "lead_id": "lead-1",
        "status": "qualified",
        "service": "garage door repair",
    }
    assert task["transcript_refs"] == ["message-1", "message-2"]
    assert task["evidence_ids"] == ["faq-1", "policy-2"]
    assert task["proposed_reply"] == "I can check that policy with the office."
    assert task["required_action"] == "approve_or_no_send"


@pytest.mark.asyncio
async def test_operator_can_edit_approve_and_send_with_audit_record() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[{"task_id": "review-1", "tenant_id": "tenant-1", "status": "open"}]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/operator/reviews/review-1/approve",
            headers=AUTH_HEADERS,
            json={
                "original_draft": "Original draft with private details",
                "final_message": "Edited message ready to send",
                "reason_code": "operator_edit",
            },
        )
        listed = await client.get("/operator/reviews", headers=AUTH_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "operator-1"
    assert body["action_at"]
    assert body["approved_at"]
    assert (
        body["original_draft_hash"]
        == hashlib.sha256(b"Original draft with private details").hexdigest()
    )
    assert body["final_message_hash"] == hashlib.sha256(b"Edited message ready to send").hexdigest()
    assert body["reason_code"] == "operator_edit"
    assert body["send_status"] == "sent"
    assert body["final_status"] == "sent"
    assert listed.json()["tasks"][0]["status"] == "sent"


@pytest.mark.asyncio
async def test_operator_can_mark_no_send_with_audit_record() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[{"task_id": "review-2", "tenant_id": "tenant-1", "status": "open"}]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/operator/reviews/review-2/no-send",
            headers=AUTH_HEADERS,
            json={
                "original_draft": "Draft that should not be sent",
                "reason_code": "unsafe_or_wrong",
            },
        )
        listed = await client.get("/operator/reviews", headers=AUTH_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "operator-1"
    assert body["action_at"]
    assert (
        body["original_draft_hash"] == hashlib.sha256(b"Draft that should not be sent").hexdigest()
    )
    assert body["final_message_hash"] == hashlib.sha256(b"").hexdigest()
    assert body["reason_code"] == "unsafe_or_wrong"
    assert body["send_status"] == "no_send"
    assert body["final_status"] == "no_send"
    assert listed.json()["tasks"][0]["status"] == "no_send"


@pytest.mark.asyncio
async def test_operator_console_rejects_unauthorized_access() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {
                "task_id": "review-1",
                "tenant_id": "tenant-1",
                "lead_summary": {"lead_id": "lead-1"},
                "proposed_reply": "Private draft",
            }
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        review_response = await client.get("/operator/reviews")
        approve_response = await client.post(
            "/operator/reviews/review-1/approve",
            json={
                "original_draft": "Private draft",
                "final_message": "Final draft",
                "reason_code": "operator_edit",
            },
        )
        no_send_response = await client.post(
            "/operator/reviews/review-1/no-send",
            json={"original_draft": "Private draft", "reason_code": "unsafe_or_wrong"},
        )

    assert review_response.status_code == 401
    assert approve_response.status_code == 401
    assert no_send_response.status_code == 401


@pytest.mark.asyncio
async def test_operator_console_keeps_outcome_labels_available() -> None:
    app = create_app()
    app.state.outcome_store = OutcomeStore()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/operator/outcomes",
            headers=AUTH_HEADERS,
            json={"lead_id": "lead-1", "label": "booked", "labeled_on": "2026-05-20"},
        )
        queried = await client.get(
            "/operator/outcomes?start_date=2026-05-01&end_date=2026-05-31",
            headers=AUTH_HEADERS,
        )

    assert created.status_code == 200
    assert queried.status_code == 200
    assert queried.json()["labels"] == [
        {
            "tenant_id": "tenant-1",
            "lead_id": "lead-1",
            "label": "booked",
            "labeled_on": "2026-05-20",
        }
    ]
