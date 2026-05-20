from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.operator.auth import OPERATOR_TEST_TOKEN
from lead_sla_agent.retrieval.chunking import INDEX_SCHEMA_VERSION

AUTH_HEADERS = {"authorization": "Bearer " + OPERATOR_TEST_TOKEN}


@pytest.mark.asyncio
async def test_operator_can_upload_list_disable_and_reindex_knowledge() -> None:
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/operator/knowledge",
            headers=AUTH_HEADERS,
            json={
                "source_document_id": "policy-1",
                "source_title": "Booking Policy",
                "text": "# Booking\nSame-day appointments are available.",
                "effective_date": "2026-05-20",
                "approved_knowledge": True,
            },
        )
        listed = await client.get("/operator/knowledge", headers=AUTH_HEADERS)
        disabled = await client.post(
            "/operator/knowledge/policy-1/disable",
            headers=AUTH_HEADERS,
        )
        reindexed = await client.post("/operator/knowledge/reindex", headers=AUTH_HEADERS)

    assert created.status_code == 200
    assert created.json()["tenant_id"] == "tenant-1"
    assert listed.status_code == 200
    assert listed.json()["documents"][0]["source_document_id"] == "policy-1"
    assert disabled.status_code == 200
    assert disabled.json()["disabled"] is True
    assert reindexed.status_code == 200
    assert reindexed.json()["actor_id"] == "operator-1"
    assert reindexed.json()["corpus_version"] == "corpus-v1"
    assert reindexed.json()["index_schema_version"] == INDEX_SCHEMA_VERSION
    assert reindexed.json()["active_document_count"] == 0


@pytest.mark.asyncio
async def test_knowledge_routes_require_auth() -> None:
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/operator/knowledge")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_rejects_raw_customer_transcript_unless_approved() -> None:
    app = create_app()
    transcript_payload = {
        "source_document_id": "transcript-1",
        "source_title": "Customer Transcript",
        "text": "Customer: my private appointment details\nAgent: confirmed",
        "effective_date": "2026-05-20",
        "approved_knowledge": False,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rejected = await client.post(
            "/operator/knowledge",
            headers=AUTH_HEADERS,
            json=transcript_payload,
        )
        accepted = await client.post(
            "/operator/knowledge",
            headers=AUTH_HEADERS,
            json={**transcript_payload, "approved_knowledge": True},
        )

    assert rejected.status_code == 400
    assert rejected.json()["detail"] == (
        "raw customer transcript data must be marked as approved knowledge"
    )
    assert accepted.status_code == 200
    assert accepted.json()["approved_knowledge"] is True
