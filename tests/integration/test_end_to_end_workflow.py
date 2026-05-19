from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest

from lead_sla_agent.conversation.loop import ConversationRuntime
from lead_sla_agent.intake.schemas import NormalizedInboundEvent
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore
from lead_sla_agent.retrieval.documents import FetchedKnowledgeDocument, SourceDocumentRef
from lead_sla_agent.retrieval.embeddings import DeterministicHashEmbeddingClient
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex, KnowledgeIngestionPipeline
from lead_sla_agent.retrieval.query import InMemoryHumanReviewSink, RetrievalQueryService
from lead_sla_agent.tools.messaging import FakeMessagingAdapter
from lead_sla_agent.workers.outbound import LeadWorkflow

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000015")


def inbound_event(message: str) -> NormalizedInboundEvent:
    return NormalizedInboundEvent(
        tenant_id=TENANT_ID,
        source_event_id=str(uuid.uuid4()),
        channel="email",
        payload_hash="hash",
        received_at=datetime.now(tz=UTC),
        contact_name="Test Lead",
        contact_email="lead@example.test",
        contact_phone="+15550101010",
        message=message,
    )


async def workflow() -> LeadWorkflow:
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)
    await pipeline.ingest_markdown_document(
        FetchedKnowledgeDocument(
            ref=SourceDocumentRef(TENANT_ID, "faq", "FAQ", date(2026, 5, 19)),
            text="# Booking\nSame-day appointments are available.",
        )
    )
    retrieval = RetrievalQueryService(index, InMemoryHumanReviewSink())
    return LeadWorkflow(
        runtime=ConversationRuntime(retrieval=retrieval),
        messaging=FakeMessagingAdapter(),
        review_store=HumanReviewTaskStore(),
    )


@pytest.mark.asyncio
async def test_supported_question_sends_grounded_reply() -> None:
    result = await (await workflow()).process_inbound_event(
        inbound_event("Are same-day appointments available?"),
        asks_policy_question=True,
    )

    assert result.lead_id
    assert result.evidence_count == 1
    assert result.outbound_draft
    assert result.send_result is not None
    assert result.send_result.status == "sent"
    assert result.human_review_count == 0


@pytest.mark.asyncio
async def test_regulated_advice_creates_review_without_send() -> None:
    result = await (await workflow()).process_inbound_event(
        inbound_event("Can you provide legal advice?"),
        asks_policy_question=True,
    )

    assert result.lead_id
    assert result.send_result is None
    assert result.human_review_count == 1
    assert result.termination_reason == "unsupported_question"


@pytest.mark.asyncio
async def test_workflow_records_latency_and_termination_reason() -> None:
    result = await (await workflow()).process_inbound_event(
        inbound_event("Can you provide legal advice?"),
        asks_policy_question=True,
    )

    assert result.first_response_latency_ms >= 0
    assert result.termination_reason == "unsupported_question"
