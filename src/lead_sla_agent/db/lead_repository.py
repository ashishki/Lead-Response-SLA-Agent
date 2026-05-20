"""Lead and conversation repository helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import Conversation, Lead
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.intake.schemas import NormalizedInboundEvent
from lead_sla_agent.observability.tracing import get_tracer


class RepositoryPersistenceError(RuntimeError):
    """PII-safe repository persistence failure."""


@dataclass(frozen=True)
class LeadRecord:
    id: uuid.UUID
    tenant_id: uuid.UUID
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    source_channel: str
    status: str


@dataclass(frozen=True)
class ConversationRecord:
    id: uuid.UUID
    tenant_id: uuid.UUID
    lead_id: uuid.UUID
    status: str


@dataclass(frozen=True)
class LeadConversationRecord:
    lead: LeadRecord
    conversation: ConversationRecord


class InMemoryLeadRepository:
    """Tenant-scoped repository used by local integration tests."""

    def __init__(self) -> None:
        self.leads: dict[uuid.UUID, LeadRecord] = {}
        self.conversations: dict[uuid.UUID, ConversationRecord] = {}

    async def create_from_event(self, event: NormalizedInboundEvent) -> LeadConversationRecord:
        lead = LeadRecord(
            id=uuid.uuid4(),
            tenant_id=event.tenant_id,
            contact_name=event.contact_name,
            contact_email=event.contact_email,
            contact_phone=event.contact_phone,
            source_channel=event.channel,
            status="new",
        )
        conversation = ConversationRecord(
            id=uuid.uuid4(),
            tenant_id=event.tenant_id,
            lead_id=lead.id,
            status="open",
        )
        self.leads[lead.id] = lead
        self.conversations[conversation.id] = conversation
        return LeadConversationRecord(lead=lead, conversation=conversation)

    async def get_lead(self, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> LeadRecord | None:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        lead = self.leads.get(lead_id)
        if lead is None or lead.tenant_id != tenant_id:
            return None
        return lead


class LeadRepository:
    """PostgreSQL-backed lead and conversation repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tracer = get_tracer(__name__)

    async def create_from_event(self, event: NormalizedInboundEvent) -> LeadConversationRecord:
        tenant_id = _require_tenant_id(event.tenant_id)

        with self.tracer.start_as_current_span("db.lead.create_from_event"):
            await apply_tenant_context(self.session, tenant_id)
            lead = Lead(
                tenant_id=tenant_id,
                contact_name=event.contact_name,
                contact_email=event.contact_email,
                contact_phone=event.contact_phone,
                source_channel=event.channel,
                status="new",
            )
            self.session.add(lead)
            await _safe_flush(self.session)

            conversation = Conversation(
                tenant_id=tenant_id,
                lead_id=lead.id,
                status="open",
            )
            self.session.add(conversation)
            await _safe_flush(self.session)

        return LeadConversationRecord(
            lead=_lead_record(lead),
            conversation=_conversation_record(conversation),
        )

    async def get_lead(self, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> LeadRecord | None:
        tenant_id = _require_tenant_id(tenant_id)
        statement = select(Lead).where(Lead.tenant_id == tenant_id, Lead.id == lead_id)

        with self.tracer.start_as_current_span("db.lead.get"):
            await apply_tenant_context(self.session, tenant_id)
            result = await self.session.execute(statement)
            lead = result.scalar_one_or_none()

        return _lead_record(lead) if lead is not None else None

    async def get_conversation(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> ConversationRecord | None:
        tenant_id = _require_tenant_id(tenant_id)
        statement = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.id == conversation_id,
        )

        with self.tracer.start_as_current_span("db.conversation.get"):
            await apply_tenant_context(self.session, tenant_id)
            result = await self.session.execute(statement)
            conversation = result.scalar_one_or_none()

        return _conversation_record(conversation) if conversation is not None else None


def _require_tenant_id(tenant_id: uuid.UUID | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    return tenant_id


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise RepositoryPersistenceError("repository persistence failed") from None


def _lead_record(lead: Lead) -> LeadRecord:
    return LeadRecord(
        id=lead.id,
        tenant_id=lead.tenant_id,
        contact_name=lead.contact_name,
        contact_email=lead.contact_email,
        contact_phone=lead.contact_phone,
        source_channel=lead.source_channel,
        status=lead.status,
    )


def _conversation_record(conversation: Conversation) -> ConversationRecord:
    return ConversationRecord(
        id=conversation.id,
        tenant_id=conversation.tenant_id,
        lead_id=conversation.lead_id,
        status=conversation.status,
    )
