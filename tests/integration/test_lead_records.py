from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from lead_sla_agent.db.lead_repository import InMemoryLeadRepository
from lead_sla_agent.db.transcript_repository import InMemoryTranscriptRepository
from lead_sla_agent.intake.lead_service import LeadService
from lead_sla_agent.intake.schemas import NormalizedInboundEvent
from lead_sla_agent.observability.pii import REDACTED_VALUE

TENANT_A = uuid.UUID("00000000-0000-4000-8000-00000000000a")
TENANT_B = uuid.UUID("00000000-0000-4000-8000-00000000000b")


def normalized_event(tenant_id: uuid.UUID = TENANT_A) -> NormalizedInboundEvent:
    return NormalizedInboundEvent(
        tenant_id=tenant_id,
        source_event_id="source-1",
        channel="website_form",
        payload_hash="abc123",
        received_at=datetime.now(tz=UTC),
        contact_name="Test Lead",
        contact_email="lead@example.test",
        contact_phone="+15550101010",
        message="Need an appointment tomorrow",
    )


@pytest.mark.asyncio
async def test_normalized_event_creates_lead_and_conversation() -> None:
    lead_repository = InMemoryLeadRepository()
    transcript_repository = InMemoryTranscriptRepository()
    service = LeadService(lead_repository, transcript_repository)

    result = await service.create_from_normalized_event(normalized_event())

    assert result.lead.contact_name == "Test Lead"
    assert result.lead.contact_email == "lead@example.test"
    assert result.lead.contact_phone == "+15550101010"
    assert result.lead.source_channel == "website_form"
    assert result.lead.status == "new"
    assert result.conversation.lead_id == result.lead.id
    assert result.conversation.tenant_id == result.lead.tenant_id


@pytest.mark.asyncio
async def test_transcript_rows_store_redacted_preview() -> None:
    lead_repository = InMemoryLeadRepository()
    transcript_repository = InMemoryTranscriptRepository()
    service = LeadService(lead_repository, transcript_repository)

    result = await service.create_from_normalized_event(
        normalized_event(),
        provider_message_id="provider-message-1",
    )
    outbound = await transcript_repository.append_message(
        tenant_id=result.lead.tenant_id,
        conversation_id=result.conversation.id,
        role="outbound",
        channel="website_form",
        content="Thanks, we received your request",
        provider_message_id="provider-message-2",
    )

    inbound = result.inbound_message
    assert inbound is not None
    assert inbound.role == "inbound"
    assert inbound.channel == "website_form"
    assert inbound.provider_message_id == "provider-message-1"
    assert inbound.content_hash
    assert inbound.redacted_preview == REDACTED_VALUE
    assert outbound.role == "outbound"
    assert outbound.provider_message_id == "provider-message-2"
    assert outbound.content_hash != inbound.content_hash
    assert outbound.redacted_preview == REDACTED_VALUE


@pytest.mark.asyncio
async def test_lead_repository_enforces_tenant_scope() -> None:
    lead_repository = InMemoryLeadRepository()
    transcript_repository = InMemoryTranscriptRepository()
    service = LeadService(lead_repository, transcript_repository)

    result = await service.create_from_normalized_event(normalized_event(TENANT_A))

    assert await lead_repository.get_lead(TENANT_A, result.lead.id) == result.lead
    assert await lead_repository.get_lead(TENANT_B, result.lead.id) is None
