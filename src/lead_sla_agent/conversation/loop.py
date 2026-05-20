"""Bounded conversation turn runtime."""

from __future__ import annotations

from dataclasses import dataclass

from lead_sla_agent.conversation.model_io import (
    ACKNOWLEDGEMENT_PROMPT_VERSION,
    QUALIFICATION_PROMPT_VERSION,
    model_output_record,
    qualifying_question_for,
)
from lead_sla_agent.conversation.policy import (
    POLICY_VERSION,
    AllowedAction,
    PolicyDecision,
    TerminationReason,
    can_draft_customer_reply,
    policy_decision_for_retrieval_status,
)
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
            output_record = model_output_record(
                output_text=question,
                prompt_version=QUALIFICATION_PROMPT_VERSION,
                policy_decision=PolicyDecision.ASK_FOR_QUALIFICATION.value,
            )
            state.audit_events.append(
                {
                    "event_type": "outbound_draft",
                    "action": AllowedAction.ASK_QUALIFYING_QUESTION.value,
                    "redacted_preview": "[redacted]",
                    "model_name": output_record.model_name,
                    "prompt_version": output_record.prompt_version,
                    "schema_version": output_record.schema_version,
                    "policy_version": POLICY_VERSION,
                    "policy_decision": output_record.policy_decision,
                }
            )
            return ConversationTurnResult(
                action=AllowedAction.ASK_QUALIFYING_QUESTION,
                outbound_draft=question,
                termination_reason=None,
            )

        if inbound.asks_policy_question and self.retrieval is not None:
            retrieval_result = await self.retrieval.retrieve(state.tenant_id, inbound.message_text)
            policy_decision = policy_decision_for_retrieval_status(retrieval_result.status)
            if not can_draft_customer_reply(retrieval_result.status):
                state.audit_events.append(
                    {
                        "event_type": "human_review_task",
                        "reason": TerminationReason.UNSUPPORTED_QUESTION.value,
                        "policy_version": POLICY_VERSION,
                        "policy_decision": policy_decision.value,
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

        output_record = model_output_record(
            output_text="Thanks, we received your request.",
            prompt_version=ACKNOWLEDGEMENT_PROMPT_VERSION,
            policy_decision=PolicyDecision.ACKNOWLEDGE_ALLOWED.value,
        )
        state.audit_events.append(
            {
                "event_type": "outbound_draft",
                "action": AllowedAction.ACKNOWLEDGE.value,
                "redacted_preview": "[redacted]",
                "model_name": output_record.model_name,
                "prompt_version": output_record.prompt_version,
                "schema_version": output_record.schema_version,
                "policy_version": POLICY_VERSION,
                "policy_decision": output_record.policy_decision,
            }
        )
        return ConversationTurnResult(
            action=AllowedAction.ACKNOWLEDGE,
            outbound_draft=output_record.output_text,
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
