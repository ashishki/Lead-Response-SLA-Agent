"""Bounded conversation turn runtime."""

from __future__ import annotations

from dataclasses import dataclass

from lead_sla_agent.conversation.model_io import qualifying_question_for
from lead_sla_agent.conversation.policy import AllowedAction, TerminationReason
from lead_sla_agent.conversation.state import (
    DEFAULT_MAX_AUTONOMOUS_TURNS,
    ConversationInput,
    ConversationState,
)
from lead_sla_agent.retrieval.query import RetrievalQueryService


@dataclass(frozen=True)
class ConversationTurnResult:
    action: AllowedAction
    outbound_draft: str | None
    termination_reason: TerminationReason | None


class ConversationRuntime:
    """One-turn bounded runtime over deterministic policy decisions."""

    def __init__(
        self,
        retrieval: RetrievalQueryService | None = None,
        max_autonomous_turns: int = DEFAULT_MAX_AUTONOMOUS_TURNS,
    ) -> None:
        self.retrieval = retrieval
        self.max_autonomous_turns = max_autonomous_turns

    async def run_turn(
        self,
        state: ConversationState,
        inbound: ConversationInput,
    ) -> ConversationTurnResult:
        if state.turn_count >= self.max_autonomous_turns:
            return self._terminate(state, TerminationReason.BUDGET_EXCEEDED)

        state.turn_count += 1
        missing_fields = sorted(state.required_fields - set(state.collected_fields))
        if missing_fields:
            question = qualifying_question_for(missing_fields[0])
            state.audit_events.append(
                {
                    "event_type": "outbound_draft",
                    "action": AllowedAction.ASK_QUALIFYING_QUESTION.value,
                    "redacted_preview": "[redacted]",
                }
            )
            return ConversationTurnResult(
                action=AllowedAction.ASK_QUALIFYING_QUESTION,
                outbound_draft=question,
                termination_reason=None,
            )

        if inbound.asks_policy_question and self.retrieval is not None:
            retrieval_result = await self.retrieval.retrieve(state.tenant_id, inbound.message_text)
            if retrieval_result.status == "insufficient_evidence":
                state.audit_events.append(
                    {
                        "event_type": "human_review_task",
                        "reason": TerminationReason.UNSUPPORTED_QUESTION.value,
                    }
                )
                return self._terminate(state, TerminationReason.UNSUPPORTED_QUESTION)

            state.audit_events.append(
                {
                    "event_type": "retrieval_evidence",
                    "evidence_ids": [
                        evidence.source_document_id for evidence in retrieval_result.evidence
                    ],
                }
            )
            return ConversationTurnResult(
                action=AllowedAction.ANSWER_WITH_EVIDENCE,
                outbound_draft=None,
                termination_reason=None,
            )

        return ConversationTurnResult(
            action=AllowedAction.ACKNOWLEDGE,
            outbound_draft="Thanks, we received your request.",
            termination_reason=None,
        )

    def _terminate(
        self,
        state: ConversationState,
        reason: TerminationReason,
    ) -> ConversationTurnResult:
        state.terminated = True
        state.termination_reason = reason.value
        state.audit_events.append({"event_type": "conversation_terminated", "reason": reason.value})
        return ConversationTurnResult(
            action=AllowedAction.CREATE_HUMAN_REVIEW_HANDOFF,
            outbound_draft=None,
            termination_reason=reason,
        )
