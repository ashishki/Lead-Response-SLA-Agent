"""Signed public webhook routes."""

from __future__ import annotations

import uuid
from typing import Protocol

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError

from lead_sla_agent.config import get_settings
from lead_sla_agent.intake.normalizer import normalize_inbound_event
from lead_sla_agent.intake.schemas import (
    InboundWebhookPayload,
    NormalizedInboundEvent,
    StoredWebhookResult,
)
from lead_sla_agent.intake.signatures import (
    PROVIDER_HEADER,
    SIGNATURE_HEADER,
    verify_provider_signature,
    verify_signature,
)


class WebhookStore(Protocol):
    async def accept_event(self, event: NormalizedInboundEvent) -> StoredWebhookResult:
        """Persist or return an idempotent inbound event result."""


class InMemoryWebhookStore:
    """Small injectable store used by tests until DB repositories own intake persistence."""

    def __init__(self) -> None:
        self.provider_events: dict[tuple[uuid.UUID, str], dict[str, object]] = {}
        self.leads: dict[uuid.UUID, dict[str, object]] = {}
        self.conversations: dict[uuid.UUID, dict[str, object]] = {}
        self.audit_events: list[dict[str, object]] = []

    async def accept_event(self, event: NormalizedInboundEvent) -> StoredWebhookResult:
        event_key = (event.tenant_id, event.source_event_id)
        existing_event = self.provider_events.get(event_key)
        if existing_event is not None:
            return StoredWebhookResult(
                provider_event_id=existing_event["id"],
                lead_id=existing_event["lead_id"],
                conversation_id=existing_event["conversation_id"],
                replayed=True,
            )

        provider_event_id = uuid.uuid4()
        lead_id = uuid.uuid4()
        conversation_id = uuid.uuid4()
        self.provider_events[event_key] = {
            "id": provider_event_id,
            "tenant_id": event.tenant_id,
            "source_event_id": event.source_event_id,
            "channel": event.channel,
            "payload_hash": event.payload_hash,
            "received_at": event.received_at,
            "lead_id": lead_id,
            "conversation_id": conversation_id,
        }
        self.leads[lead_id] = {
            "id": lead_id,
            "tenant_id": event.tenant_id,
            "source_channel": event.channel,
            "status": "new",
        }
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "tenant_id": event.tenant_id,
            "lead_id": lead_id,
            "status": "open",
        }
        self.audit_events.append(
            {
                "tenant_id": event.tenant_id,
                "event_type": "webhook.accepted",
                "provider_event_id": provider_event_id,
            }
        )
        return StoredWebhookResult(
            provider_event_id=provider_event_id,
            lead_id=lead_id,
            conversation_id=conversation_id,
            replayed=False,
        )

    def row_counts(self) -> dict[str, int]:
        """Return row-count-like values for integration tests."""
        return {
            "provider_event": len(self.provider_events),
            "lead": len(self.leads),
            "conversation": len(self.conversations),
            "audit_event": len(self.audit_events),
        }


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/inbound", status_code=status.HTTP_202_ACCEPTED)
async def receive_inbound_webhook(request: Request) -> dict[str, str | bool]:
    raw_body = await request.body()
    settings = get_settings()
    signature = request.headers.get(SIGNATURE_HEADER)
    provider = request.headers.get(PROVIDER_HEADER)
    if provider:
        signature_valid = verify_provider_signature(
            provider,
            raw_body,
            request.headers,
            settings.webhook_shared_secret,
        )
    else:
        signature_valid = verify_signature(raw_body, signature, settings.webhook_shared_secret)
    if not signature_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid webhook signature",
        )

    try:
        payload = InboundWebhookPayload.model_validate_json(raw_body)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid webhook payload",
        ) from exc

    event = normalize_inbound_event(payload, raw_body)
    store: WebhookStore = request.app.state.webhook_store
    result = await store.accept_event(event)
    return {
        "provider_event_id": str(result.provider_event_id),
        "lead_id": str(result.lead_id),
        "conversation_id": str(result.conversation_id),
        "replayed": result.replayed,
    }
