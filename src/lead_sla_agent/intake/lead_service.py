"""Lead creation service for normalized inbound events."""

from __future__ import annotations

from dataclasses import dataclass

from lead_sla_agent.db.lead_repository import (
    ConversationRecord,
    InMemoryLeadRepository,
    LeadRecord,
)
from lead_sla_agent.db.transcript_repository import (
    InMemoryTranscriptRepository,
    TranscriptMessageRecord,
)
from lead_sla_agent.intake.schemas import NormalizedInboundEvent


@dataclass(frozen=True)
class LeadCreationResult:
    lead: LeadRecord
    conversation: ConversationRecord
    inbound_message: TranscriptMessageRecord | None


class LeadService:
    """Convert normalized inbound events into lead, conversation, and transcript state."""

    def __init__(
        self,
        lead_repository: InMemoryLeadRepository,
        transcript_repository: InMemoryTranscriptRepository,
    ) -> None:
        self.lead_repository = lead_repository
        self.transcript_repository = transcript_repository

    async def create_from_normalized_event(
        self,
        event: NormalizedInboundEvent,
        provider_message_id: str | None = None,
    ) -> LeadCreationResult:
        created = await self.lead_repository.create_from_event(event)
        inbound_message = None
        if event.message:
            inbound_message = await self.transcript_repository.append_message(
                tenant_id=event.tenant_id,
                conversation_id=created.conversation.id,
                role="inbound",
                channel=event.channel,
                content=event.message,
                provider_message_id=provider_message_id,
            )

        return LeadCreationResult(
            lead=created.lead,
            conversation=created.conversation,
            inbound_message=inbound_message,
        )
