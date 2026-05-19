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
