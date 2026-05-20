"""Allowed action and termination policy."""

from __future__ import annotations

from enum import StrEnum


class AllowedAction(StrEnum):
    ACKNOWLEDGE = "acknowledge"
    ASK_QUALIFYING_QUESTION = "ask_qualifying_question"
    ANSWER_WITH_EVIDENCE = "answer_with_evidence"
    PROPOSE_SLOT = "propose_slot"
    CREATE_OR_UPDATE_LEAD = "create_or_update_lead"
    BOOK_ACCEPTED_SLOT = "book_accepted_slot"
    CREATE_HUMAN_REVIEW_HANDOFF = "create_human_review_handoff"


class TerminationReason(StrEnum):
    BOOKED = "booked"
    QUALIFIED_HANDOFF = "qualified_handoff"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    UNSUPPORTED_QUESTION = "unsupported_question"
    NO_RESPONSE_TIMEOUT = "no_response_timeout"
    BUDGET_EXCEEDED = "budget_exceeded"
    PROVIDER_ERROR = "provider_error"


ALLOWED_ACTIONS = {action.value for action in AllowedAction}
POLICY_VERSION = "conversation-policy-v1"


class PolicyDecision(StrEnum):
    ANSWER_ALLOWED = "answer_allowed"
    ASK_FOR_QUALIFICATION = "ask_for_qualification"
    ACKNOWLEDGE_ALLOWED = "acknowledge_allowed"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


def policy_decision_for_retrieval_status(status: str) -> PolicyDecision:
    if status == "insufficient_evidence":
        return PolicyDecision.HUMAN_REVIEW_REQUIRED
    return PolicyDecision.ANSWER_ALLOWED


def can_draft_customer_reply(retrieval_status: str) -> bool:
    """Return whether retrieval status permits customer-facing answer text."""
    return policy_decision_for_retrieval_status(retrieval_status) == PolicyDecision.ANSWER_ALLOWED
