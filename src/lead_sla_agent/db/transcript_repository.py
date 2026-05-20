"""Transcript repository helpers."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import Message
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.observability.tracing import get_tracer


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


class TranscriptRepository:
    """PostgreSQL-backed transcript repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def append_message(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
        role: str,
        channel: str,
        content: str,
        provider_message_id: str | None = None,
    ) -> TranscriptMessageRecord:
        tenant_id = _require_tenant_id(tenant_id)

        with self.tracer.start_as_current_span("db.transcript.append_message"):
            await apply_tenant_context(self.session, tenant_id)
            message = Message(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                role=role,
                channel=channel,
                provider_message_id=provider_message_id,
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                redacted_preview=REDACTED_VALUE,
            )
            self.session.add(message)
            await _safe_flush(self.session)

        return _message_record(message)

    async def list_messages(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> list[TranscriptMessageRecord]:
        tenant_id = _require_tenant_id(tenant_id)
        statement = (
            select(Message)
            .where(Message.tenant_id == tenant_id, Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )

        with self.tracer.start_as_current_span("db.transcript.list_messages"):
            await apply_tenant_context(self.session, tenant_id)
            result = await self.session.execute(statement)

        return [_message_record(message) for message in result.scalars().all()]


def _require_tenant_id(tenant_id: uuid.UUID | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    return tenant_id


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise RuntimeError("repository persistence failed") from None


def _message_record(message: Message) -> TranscriptMessageRecord:
    return TranscriptMessageRecord(
        id=message.id,
        tenant_id=message.tenant_id,
        conversation_id=message.conversation_id,
        role=message.role,
        channel=message.channel,
        provider_message_id=message.provider_message_id,
        content_hash=message.content_hash,
        redacted_preview=message.redacted_preview,
    )
