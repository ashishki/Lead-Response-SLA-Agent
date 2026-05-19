from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.operator.auth import OPERATOR_TEST_TOKEN
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

AUTH_HEADERS = {"authorization": f"Bearer {OPERATOR_TEST_TOKEN}"}


@pytest.mark.asyncio
async def test_operator_can_list_review_tasks() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {
                "task_id": "review-1",
                "tenant_id": "tenant-1",
                "lead_summary": {"status": "new"},
                "handoff_reason": "unsupported_question",
                "transcript_refs": ["message-1"],
                "evidence_ids": ["faq-1"],
                "proposed_reply": "Draft reply",
            }
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/operator/reviews", headers=AUTH_HEADERS)

    assert response.status_code == 200
    task = response.json()["tasks"][0]
    assert task["lead_summary"] == {"status": "new"}
    assert task["handoff_reason"] == "unsupported_question"
    assert task["transcript_refs"] == ["message-1"]
    assert task["evidence_ids"] == ["faq-1"]
    assert task["proposed_reply"] == "Draft reply"


@pytest.mark.asyncio
async def test_operator_routes_require_auth() -> None:
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/operator/reviews")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_approval_records_audit_fields_before_send() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/operator/reviews/review-1/approve",
            headers=AUTH_HEADERS,
            json={
                "original_draft": "Original draft with PII",
                "final_message": "Final approved message",
                "reason_code": "operator_edit",
            },
        )

    body = response.json()
    assert response.status_code == 200
    assert body["actor_id"] == "operator-1"
    assert body["approved_at"]
    assert body["original_draft_hash"]
    assert body["final_message_hash"]
    assert body["reason_code"] == "operator_edit"
    assert body["send_status"] == "sent"


@pytest.mark.asyncio
async def test_outcome_labels_are_queryable() -> None:
    app = create_app()
    app.state.outcome_store = OutcomeStore()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/operator/outcomes",
            headers=AUTH_HEADERS,
            json={"lead_id": "lead-1", "label": "booked", "labeled_on": "2026-05-19"},
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
            "labeled_on": "2026-05-19",
        }
    ]
