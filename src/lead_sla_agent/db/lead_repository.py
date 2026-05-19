"""Lead and conversation repository helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from lead_sla_agent.intake.schemas import NormalizedInboundEvent


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
