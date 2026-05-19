"""Normalize provider webhook payloads into internal intake events."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from lead_sla_agent.intake.schemas import InboundWebhookPayload, NormalizedInboundEvent


def normalize_inbound_event(
    payload: InboundWebhookPayload,
    raw_body: bytes,
) -> NormalizedInboundEvent:
    """Create the internal event shape from an accepted signed webhook payload."""
    return NormalizedInboundEvent(
        tenant_id=payload.tenant_id,
        source_event_id=payload.source_event_id,
        channel=payload.channel,
        payload_hash=hashlib.sha256(raw_body).hexdigest(),
        received_at=datetime.now(tz=UTC),
        contact_name=payload.contact_name,
        contact_email=str(payload.contact_email) if payload.contact_email else None,
        contact_phone=payload.contact_phone,
        message=payload.message,
    )
