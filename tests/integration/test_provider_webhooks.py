from __future__ import annotations

import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.api.webhooks import InMemoryWebhookStore
from lead_sla_agent.intake.normalizer import normalize_provider_inbound_event
from lead_sla_agent.intake.schemas import InboundWebhookPayload
from lead_sla_agent.intake.signatures import (
    PROVIDER_HEADER,
    SIGNATURE_HEADER,
    TELEGRAM_SECRET_HEADER,
    WHATSAPP_SIGNATURE_HEADER,
    build_provider_signature,
    verify_provider_signature,
)
from lead_sla_agent.observability.pii import hash_identifier, redact_mapping

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def _webhook_body(provider: str = "whatsapp", source_event_id: str = "evt-provider-1") -> bytes:
    return json.dumps(
        {
            "tenant_id": str(TENANT_ID),
            "source_event_id": source_event_id,
            "channel": provider,
            "contact_name": "Private Lead",
            "contact_email": "lead@example.test",
            "contact_phone": "+15550101010",
            "message": "Need an appointment",
        },
        sort_keys=True,
    ).encode("utf-8")


@pytest.mark.parametrize(
    ("provider", "signature_header"),
    [
        ("email", SIGNATURE_HEADER),
        ("whatsapp", WHATSAPP_SIGNATURE_HEADER),
        ("telegram", TELEGRAM_SECRET_HEADER),
    ],
)
def test_provider_signature_matrix_accepts_valid_and_rejects_invalid_signatures(
    provider: str,
    signature_header: str,
) -> None:
    raw_body = _webhook_body(provider)
    valid_headers = {
        signature_header: build_provider_signature(provider, raw_body, "test-webhook-secret")
    }
    invalid_headers = {signature_header: "invalid"}

    assert verify_provider_signature(provider, raw_body, valid_headers, "test-webhook-secret")
    assert not verify_provider_signature(provider, raw_body, invalid_headers, "test-webhook-secret")


@pytest.mark.asyncio
async def test_invalid_provider_signature_writes_no_rows() -> None:
    app = create_app()
    store = InMemoryWebhookStore()
    app.state.webhook_store = store
    raw_body = _webhook_body("whatsapp")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/inbound",
            content=raw_body,
            headers={
                "content-type": "application/json",
                PROVIDER_HEADER: "whatsapp",
                WHATSAPP_SIGNATURE_HEADER: "sha256=invalid",
            },
        )

    assert response.status_code == 401
    assert store.row_counts() == {
        "provider_event": 0,
        "lead": 0,
        "conversation": 0,
        "audit_event": 0,
    }


def test_provider_normalization_preserves_canonical_event_fields() -> None:
    raw_body = _webhook_body("whatsapp", "evt-normalized")
    payload = InboundWebhookPayload.model_validate_json(raw_body)

    event = normalize_provider_inbound_event("whatsapp", payload, raw_body)

    assert event.tenant_id == TENANT_ID
    assert event.source_event_id == "evt-normalized"
    assert event.channel == "whatsapp"
    assert event.received_at
    assert event.payload_hash


def test_provider_identifiers_are_pii_in_observability() -> None:
    scrubbed = redact_mapping(
        {
            "provider_user_id": "provider-user-123",
            "provider_message_id": "provider-message-456",
        }
    )

    assert scrubbed == {
        "provider_user_id": hash_identifier("provider-user-123"),
        "provider_message_id": hash_identifier("provider-message-456"),
    }
