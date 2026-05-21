from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.api.webhooks import InMemoryWebhookStore
from lead_sla_agent.intake.signatures import (
    PROVIDER_HEADER,
    SIGNATURE_HEADER,
    TELEGRAM_SECRET_HEADER,
    WHATSAPP_SIGNATURE_HEADER,
    build_provider_signature,
)

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
WEBHOOK_SECRET = "test-webhook-secret"
RAW_MESSAGE = "Need an urgent appointment at my house"


def _provider_body(provider: str, source_event_id: str) -> bytes:
    channel = {
        "postmark_email": "email",
        "twilio_whatsapp": "whatsapp",
        "telegram_bot": "telegram",
    }[provider]
    return json.dumps(
        {
            "tenant_id": str(TENANT_ID),
            "source_event_id": source_event_id,
            "channel": channel,
            "contact_name": "Private Lead",
            "contact_email": "lead@example.test",
            "contact_phone": "+15550101010",
            "message": RAW_MESSAGE,
        },
        sort_keys=True,
    ).encode("utf-8")


def _signature_header(provider: str, body: bytes) -> dict[str, str]:
    header_name = {
        "postmark_email": SIGNATURE_HEADER,
        "twilio_whatsapp": WHATSAPP_SIGNATURE_HEADER,
        "telegram_bot": TELEGRAM_SECRET_HEADER,
    }[provider]
    return {header_name: build_provider_signature(provider, body, WEBHOOK_SECRET)}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider",
    [
        "postmark_email",
        "twilio_whatsapp",
        "telegram_bot",
    ],
)
async def test_provider_webhook_e2e_creates_lead_transcript_and_review_task(
    provider: str,
) -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    body = _provider_body(provider, f"{provider}:evt-1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/inbound",
            content=body,
            headers={
                "content-type": "application/json",
                PROVIDER_HEADER: provider,
                **_signature_header(provider, body),
            },
        )

    assert response.status_code == 202
    assert response.json()["replayed"] is False
    assert store.workflow_counts() == {
        "provider_event": 1,
        "lead": 1,
        "conversation": 1,
        "audit_event": 1,
        "transcript": 1,
        "review_task": 1,
    }
    provider_event = next(iter(store.provider_events.values()))
    transcript = next(iter(store.transcripts.values()))
    review_task = store.review_tasks[0]
    assert provider_event["source_event_id"] == f"{provider}:evt-1"
    assert transcript["payload_hash"] == provider_event["payload_hash"]
    assert "message_hash" in transcript
    assert review_task["reason"] == "provider_webhook_inbound_review"
    assert review_task["payload_hash"] == provider_event["payload_hash"]
    assert RAW_MESSAGE not in str(provider_event)
    assert RAW_MESSAGE not in str(transcript)
    assert RAW_MESSAGE not in str(review_task)


@pytest.mark.asyncio
async def test_replayed_provider_event_is_idempotent_across_full_workflow() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    body = _provider_body("twilio_whatsapp", "twilio:evt-replay")
    headers = {
        "content-type": "application/json",
        PROVIDER_HEADER: "twilio_whatsapp",
        **_signature_header("twilio_whatsapp", body),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/webhooks/inbound", content=body, headers=headers)
        second = await client.post("/webhooks/inbound", content=body, headers=headers)

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["replayed"] is True
    assert second.json()["provider_event_id"] == first.json()["provider_event_id"]
    assert store.workflow_counts() == {
        "provider_event": 1,
        "lead": 1,
        "conversation": 1,
        "audit_event": 1,
        "transcript": 1,
        "review_task": 1,
    }


@pytest.mark.asyncio
async def test_invalid_provider_webhook_signature_rejects_before_workflow_writes() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    body = _provider_body("telegram_bot", "telegram:evt-invalid")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/inbound",
            content=body,
            headers={
                "content-type": "application/json",
                PROVIDER_HEADER: "telegram_bot",
                TELEGRAM_SECRET_HEADER: "wrong-secret",
            },
        )

    assert response.status_code == 401
    assert store.workflow_counts() == {
        "provider_event": 0,
        "lead": 0,
        "conversation": 0,
        "audit_event": 0,
        "transcript": 0,
        "review_task": 0,
    }


def test_runbook_documents_public_provider_webhook_setup_without_token_values() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "Postmark inbound webhook" in content
    assert "Twilio WhatsApp webhook" in content
    assert "Telegram Bot API webhook" in content
    assert "VPS reverse proxy" in content
    assert "X-Telegram-Bot-Api-Secret-Token" in content
    assert "Do not paste bot tokens" in content
    assert "opt-in source" in content
