from __future__ import annotations

import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.api.webhooks import InMemoryWebhookStore
from lead_sla_agent.intake.signatures import SIGNATURE_HEADER, build_signature


def _webhook_body(source_event_id: str = "evt-1") -> bytes:
    return json.dumps(
        {
            "tenant_id": str(uuid.UUID("00000000-0000-4000-8000-000000000001")),
            "source_event_id": source_event_id,
            "channel": "website_form",
            "contact_name": "Test Lead",
            "contact_email": "lead@example.test",
            "contact_phone": "+15550101010",
            "message": "Need an appointment",
        },
        sort_keys=True,
    ).encode("utf-8")


async def _post_webhook(
    client: AsyncClient,
    raw_body: bytes,
    secret: str = "test-webhook-secret",
) -> object:
    return await client.post(
        "/webhooks/inbound",
        content=raw_body,
        headers={
            "content-type": "application/json",
            SIGNATURE_HEADER: build_signature(raw_body, secret),
        },
    )


@pytest.mark.asyncio
async def test_valid_signed_webhook_persists_provider_event() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    raw_body = _webhook_body()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await _post_webhook(client, raw_body)

    assert response.status_code == 202
    assert response.json()["replayed"] is False
    assert store.row_counts() == {
        "provider_event": 1,
        "lead": 1,
        "conversation": 1,
        "audit_event": 1,
    }
    stored_event = next(iter(store.provider_events.values()))
    assert stored_event["source_event_id"] == "evt-1"
    assert stored_event["channel"] == "website_form"
    assert stored_event["payload_hash"]
    assert stored_event["received_at"]


@pytest.mark.asyncio
async def test_invalid_signature_creates_no_rows() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    raw_body = _webhook_body()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/webhooks/inbound",
            content=raw_body,
            headers={
                "content-type": "application/json",
                SIGNATURE_HEADER: "sha256=invalid",
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid webhook signature"}
    assert store.row_counts() == {
        "provider_event": 0,
        "lead": 0,
        "conversation": 0,
        "audit_event": 0,
    }


@pytest.mark.asyncio
async def test_replayed_event_is_idempotent() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    raw_body = _webhook_body(source_event_id="evt-replay")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first_response = await _post_webhook(client, raw_body)
        second_response = await _post_webhook(client, raw_body)

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert second_response.json()["replayed"] is True
    assert second_response.json()["provider_event_id"] == first_response.json()["provider_event_id"]
    assert second_response.json()["lead_id"] == first_response.json()["lead_id"]
    assert store.row_counts() == {
        "provider_event": 1,
        "lead": 1,
        "conversation": 1,
        "audit_event": 1,
    }
