"""Transcript repository helpers."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from lead_sla_agent.observability.pii import REDACTED_VALUE


@dataclass(frozen=True)
class TranscriptMessageRecord:
    id: uuid.UUID
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    channel: str
    provider_message_id: str | None
    content_hash: str
    redacted_preview: str


class InMemoryTranscriptRepository:
    """Tenant-scoped transcript repository used by local integration tests."""

    def __init__(self) -> None:
        self.messages: list[TranscriptMessageRecord] = []

    async def append_message(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
        role: str,
        channel: str,
        content: str,
        provider_message_id: str | None = None,
    ) -> TranscriptMessageRecord:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        message = TranscriptMessageRecord(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            role=role,
            channel=channel,
            provider_message_id=provider_message_id,
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            redacted_preview=REDACTED_VALUE,
        )
        self.messages.append(message)
        return message

    async def list_messages(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> list[TranscriptMessageRecord]:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        return [
            message
            for message in self.messages
            if message.tenant_id == tenant_id and message.conversation_id == conversation_id
        ]
