from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.operator.auth import issue_operator_token
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore


def _auth_headers(role: str, tenant_id: str = "tenant-1") -> dict[str, str]:
    token = issue_operator_token(actor_id=f"{role}-1", tenant_id=tenant_id, role=role)
    return {"authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_owner_and_operator_can_access_operator_routes() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {"task_id": "review-1", "tenant_id": "tenant-1", "status": "open"},
            {"task_id": "review-2", "tenant_id": "tenant-2", "status": "open"},
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        owner_response = await client.get("/operator/reviews", headers=_auth_headers("owner"))
        operator_response = await client.get("/operator/reviews", headers=_auth_headers("operator"))

    assert owner_response.status_code == 200
    assert operator_response.status_code == 200
    assert [task["task_id"] for task in owner_response.json()["tasks"]] == ["review-1"]
    assert [task["task_id"] for task in operator_response.json()["tasks"]] == ["review-1"]


@pytest.mark.asyncio
async def test_viewer_role_is_rejected_before_operator_data_access() -> None:
    app = create_app()
    app.state.review_store = ExplodingReviewStore()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/operator/reviews", headers=_auth_headers("viewer"))

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}


@pytest.mark.asyncio
async def test_invalid_or_expired_tokens_expose_no_operator_data() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {"task_id": "review-1", "tenant_id": "tenant-1", "lead_summary": {"lead_id": "lead-1"}}
        ]
    )
    expired_token = issue_operator_token(
        actor_id="operator-1",
        tenant_id="tenant-1",
        role="operator",
        expires_at=datetime.now(tz=UTC) - timedelta(minutes=1),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        missing_response = await client.get("/operator/reviews")
        malformed_response = await client.get(
            "/operator/reviews",
            headers={"authorization": "Bearer not-a-valid-token"},
        )
        expired_response = await client.get(
            "/operator/reviews",
            headers={"authorization": f"Bearer {expired_token}"},
        )

    assert missing_response.status_code == 401
    assert malformed_response.status_code == 401
    assert expired_response.status_code == 401
    assert missing_response.json() == {"detail": "unauthorized"}
    assert malformed_response.json() == {"detail": "unauthorized"}
    assert expired_response.json() == {"detail": "unauthorized"}


@pytest.mark.asyncio
async def test_token_tenant_claim_scopes_operator_data() -> None:
    app = create_app()
    app.state.review_store = HumanReviewTaskStore(
        tasks=[
            {"task_id": "tenant-1-review", "tenant_id": "tenant-1", "status": "open"},
            {"task_id": "tenant-2-review", "tenant_id": "tenant-2", "status": "open"},
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/operator/reviews",
            headers=_auth_headers("operator", tenant_id="tenant-2"),
        )

    assert response.status_code == 200
    assert response.json()["tasks"] == [
        {"task_id": "tenant-2-review", "tenant_id": "tenant-2", "status": "open"}
    ]


class ExplodingReviewStore:
    async def list_tasks(self, tenant_id: str) -> list[dict[str, Any]]:
        raise AssertionError(f"data access should not run for tenant {tenant_id}")
