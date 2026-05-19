from __future__ import annotations

import uuid
from datetime import date

import pytest

from lead_sla_agent.conversation.loop import ConversationRuntime
from lead_sla_agent.conversation.policy import AllowedAction, TerminationReason
from lead_sla_agent.conversation.state import ConversationInput, ConversationState
from lead_sla_agent.retrieval.documents import FetchedKnowledgeDocument, SourceDocumentRef
from lead_sla_agent.retrieval.embeddings import DeterministicHashEmbeddingClient
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex, KnowledgeIngestionPipeline
from lead_sla_agent.retrieval.query import InMemoryHumanReviewSink, RetrievalQueryService

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000013")


def state_with_fields(turn_count: int = 0) -> ConversationState:
    return ConversationState(
        tenant_id=TENANT_ID,
        conversation_id=uuid.uuid4(),
        lead_id=uuid.uuid4(),
        turn_count=turn_count,
        collected_fields={"contact_name": "Test Lead", "contact_phone": "+15550101010"},
    )


async def retrieval_service() -> RetrievalQueryService:
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)
    await pipeline.ingest_markdown_document(
        FetchedKnowledgeDocument(
            ref=SourceDocumentRef(TENANT_ID, "faq", "FAQ", date(2026, 5, 19)),
            text="# Booking\nSame-day appointments are available.",
        )
    )
    return RetrievalQueryService(index, InMemoryHumanReviewSink())


@pytest.mark.asyncio
async def test_missing_fields_selects_qualifying_question() -> None:
    runtime = ConversationRuntime()
    state = ConversationState(
        tenant_id=TENANT_ID,
        conversation_id=uuid.uuid4(),
        lead_id=uuid.uuid4(),
    )

    result = await runtime.run_turn(state, ConversationInput(message_text="Hi"))

    assert result.action == AllowedAction.ASK_QUALIFYING_QUESTION
    assert result.outbound_draft
    assert state.audit_events[-1]["event_type"] == "outbound_draft"


@pytest.mark.asyncio
async def test_unsupported_question_terminates_with_handoff() -> None:
    runtime = ConversationRuntime(retrieval=await retrieval_service())
    state = state_with_fields()

    result = await runtime.run_turn(
        state,
        ConversationInput(
            message_text="Can you provide legal advice?",
            asks_policy_question=True,
        ),
    )

    assert result.termination_reason == TerminationReason.UNSUPPORTED_QUESTION
    assert state.terminated is True
    assert state.termination_reason == "unsupported_question"
    assert any(event["event_type"] == "human_review_task" for event in state.audit_events)


@pytest.mark.asyncio
async def test_max_turn_budget_terminates_loop() -> None:
    runtime = ConversationRuntime(max_autonomous_turns=2)
    state = state_with_fields(turn_count=2)

    result = await runtime.run_turn(state, ConversationInput(message_text="Still here"))

    assert result.termination_reason == TerminationReason.BUDGET_EXCEEDED
    assert state.termination_reason == "budget_exceeded"
