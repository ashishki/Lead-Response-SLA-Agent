"""Conversation state types."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

AGENT_LOOP_VERSION = "agent-loop-v1"
DEFAULT_MAX_AUTONOMOUS_TURNS = 6
DEFAULT_MAX_TOOL_CALLS_PER_TURN = 3


@dataclass
class ConversationState:
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID
    lead_id: uuid.UUID
    turn_count: int = 0
    required_fields: set[str] = field(default_factory=lambda: {"contact_name", "contact_phone"})
    collected_fields: dict[str, str] = field(default_factory=dict)
    terminated: bool = False
    termination_reason: str | None = None
    audit_events: list[dict[str, object]] = field(default_factory=list)


@dataclass(frozen=True)
class ConversationInput:
    message_text: str
    asks_policy_question: bool = False
