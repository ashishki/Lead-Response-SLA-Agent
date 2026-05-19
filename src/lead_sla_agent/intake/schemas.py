"""Schemas for inbound lead intake."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InboundWebhookPayload(BaseModel):
    """Provider-neutral webhook payload accepted by the public intake route."""

    model_config = ConfigDict(extra="ignore")

    tenant_id: uuid.UUID
    source_event_id: str = Field(min_length=1, max_length=255)
    channel: str = Field(min_length=1, max_length=32)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=320)
    contact_phone: str | None = Field(default=None, max_length=64)
    message: str | None = Field(default=None, max_length=4000)


class NormalizedInboundEvent(BaseModel):
    """Internal normalized inbound event shape."""

    tenant_id: uuid.UUID
    source_event_id: str
    channel: str
    payload_hash: str
    received_at: datetime
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    message: str | None = None


class StoredWebhookResult(BaseModel):
    """Result returned after an inbound event is accepted."""

    provider_event_id: uuid.UUID
    lead_id: uuid.UUID
    conversation_id: uuid.UUID
    replayed: bool
