"""End-to-end inbound lead workflow orchestration."""

from __future__ import annotations

import time
from dataclasses import dataclass

from lead_sla_agent.conversation.loop import ConversationRuntime
from lead_sla_agent.conversation.policy import TerminationReason
from lead_sla_agent.conversation.state import ConversationInput
from lead_sla_agent.db.lead_repository import InMemoryLeadRepository
from lead_sla_agent.db.transcript_repository import InMemoryTranscriptRepository
from lead_sla_agent.intake.lead_service import LeadService
from lead_sla_agent.intake.schemas import NormalizedInboundEvent
from lead_sla_agent.observability.metrics import metrics
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore
from lead_sla_agent.tools.messaging import FakeMessagingAdapter, MessageSendResult


@dataclass(frozen=True)
class WorkflowResult:
    lead_id: str
    evidence_count: int
    outbound_draft: str | None
    send_result: MessageSendResult | None
    human_review_count: int
    first_response_latency_ms: float
    termination_reason: str


class LeadWorkflow:
    """Small orchestrator connecting intake, retrieval, conversation, and outbound send."""

    def __init__(
        self,
        runtime: ConversationRuntime,
        messaging: FakeMessagingAdapter,
        review_store: HumanReviewTaskStore,
        lead_repository: InMemoryLeadRepository | None = None,
        transcript_repository: InMemoryTranscriptRepository | None = None,
    ) -> None:
        self.runtime = runtime
        self.messaging = messaging
        self.review_store = review_store
        self.lead_repository = lead_repository or InMemoryLeadRepository()
        self.transcript_repository = transcript_repository or InMemoryTranscriptRepository()

    async def process_inbound_event(
        self,
        event: NormalizedInboundEvent,
        asks_policy_question: bool,
    ) -> WorkflowResult:
        started_at = time.perf_counter()
        lead_service = LeadService(self.lead_repository, self.transcript_repository)
        created = await lead_service.create_from_normalized_event(event)
        state = self.runtime_state(event, str(created.lead.id))
        turn = await self.runtime.run_turn(
            state,
            ConversationInput(
                message_text=event.message or "",
                asks_policy_question=asks_policy_question,
            ),
        )
        evidence_count = sum(
            len(audit_event.get("evidence_ids", []))
            for audit_event in state.audit_events
            if audit_event.get("event_type") == "retrieval_evidence"
        )

        send_result = None
        human_review_count = 0
        termination_reason = state.termination_reason or "responded"
        if state.termination_reason == TerminationReason.UNSUPPORTED_QUESTION.value:
            metrics.increment("insufficient_evidence_total")
            await self.review_store.create_human_review_task(
                conversation_id=created.conversation.id,
                handoff_reason=TerminationReason.UNSUPPORTED_QUESTION.value,
                payload={"lead_id": str(created.lead.id)},
                tenant_id=event.tenant_id,
            )
            human_review_count = 1
        else:
            message = turn.outbound_draft or "We found approved information for your question."
            send_result = await self.messaging.send_message(
                channel=event.channel,
                recipient=event.contact_email or "unknown",
                text=message,
            )
            metrics.increment("tool_call_success_total")

        outbound_draft = turn.outbound_draft or "We found approved information for your question."
        latency_ms = (time.perf_counter() - started_at) * 1000
        metrics.observe("first_response_latency_ms", latency_ms)
        metrics.increment("sla_processed_total")
        metrics.observe("retrieval_latency_ms", 0)
        metrics.increment(f"agent_termination_reason_{termination_reason}_total")
        return WorkflowResult(
            lead_id=str(created.lead.id),
            evidence_count=evidence_count,
            outbound_draft=outbound_draft,
            send_result=send_result,
            human_review_count=human_review_count,
            first_response_latency_ms=latency_ms,
            termination_reason=termination_reason,
        )

    @staticmethod
    def runtime_state(event: NormalizedInboundEvent, lead_id: str):
        from uuid import UUID, uuid4

        from lead_sla_agent.conversation.state import ConversationState

        return ConversationState(
            tenant_id=event.tenant_id,
            conversation_id=uuid4(),
            lead_id=UUID(lead_id),
            collected_fields={
                "contact_name": event.contact_name or "unknown",
                "contact_phone": event.contact_phone or "unknown",
            },
        )
