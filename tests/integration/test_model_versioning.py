from __future__ import annotations

import uuid
from dataclasses import dataclass, field

import pytest

from lead_sla_agent.conversation.loop import ConversationRuntime
from lead_sla_agent.conversation.model_io import (
    MODEL_OUTPUT_SCHEMA_VERSION,
    QUALIFICATION_PROMPT_VERSION,
    model_output_record,
)
from lead_sla_agent.conversation.policy import (
    POLICY_VERSION,
    PolicyDecision,
    TerminationReason,
    can_draft_customer_reply,
)
from lead_sla_agent.conversation.state import ConversationInput, ConversationState


def test_model_output_record_contains_version_contracts() -> None:
    record = model_output_record(
        output_text="What name should we use?",
        prompt_version=QUALIFICATION_PROMPT_VERSION,
        policy_decision=PolicyDecision.ASK_FOR_QUALIFICATION.value,
    )

    assert record.model_name == "deterministic-runtime-v1"
    assert record.prompt_version == QUALIFICATION_PROMPT_VERSION
    assert record.schema_version == MODEL_OUTPUT_SCHEMA_VERSION
    assert record.policy_decision == PolicyDecision.ASK_FOR_QUALIFICATION.value


@pytest.mark.asyncio
async def test_loop_audit_records_model_prompt_schema_and_policy_versions() -> None:
    state = ConversationState(
        tenant_id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        lead_id=uuid.uuid4(),
        collected_fields={},
    )
    runtime = ConversationRuntime()

    result = await runtime.run_turn(
        state,
        ConversationInput(message_text="Need help", asks_policy_question=False),
    )

    assert result.outbound_draft
    audit_event = state.audit_events[0]
    assert audit_event["model_name"] == "deterministic-runtime-v1"
    assert audit_event["prompt_version"] == QUALIFICATION_PROMPT_VERSION
    assert audit_event["schema_version"] == MODEL_OUTPUT_SCHEMA_VERSION
    assert audit_event["policy_version"] == POLICY_VERSION
    assert audit_event["policy_decision"] == PolicyDecision.ASK_FOR_QUALIFICATION.value


@pytest.mark.asyncio
async def test_unsupported_evidence_cannot_produce_customer_facing_text() -> None:
    state = ConversationState(
        tenant_id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        lead_id=uuid.uuid4(),
        collected_fields={"contact_name": "known", "contact_phone": "known"},
    )
    runtime = ConversationRuntime(retrieval=InsufficientEvidenceRetrieval())

    result = await runtime.run_turn(
        state,
        ConversationInput(message_text="Can you give legal advice?", asks_policy_question=True),
    )

    assert can_draft_customer_reply("insufficient_evidence") is False
    assert result.outbound_draft is None
    assert result.termination_reason == TerminationReason.UNSUPPORTED_QUESTION
    human_review_event = state.audit_events[0]
    assert human_review_event["policy_version"] == POLICY_VERSION
    assert human_review_event["policy_decision"] == PolicyDecision.HUMAN_REVIEW_REQUIRED.value


@dataclass(frozen=True)
class RetrievalResultStub:
    status: str = "insufficient_evidence"
    answer_text: str | None = None
    evidence: list[object] = field(default_factory=list)
    human_review_task: object | None = None


class InsufficientEvidenceRetrieval:
    async def retrieve(self, tenant_id: uuid.UUID, query: str) -> RetrievalResultStub:
        del tenant_id, query
        return RetrievalResultStub(evidence=[])
