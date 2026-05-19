"""Versioned tool catalog."""

from __future__ import annotations

from lead_sla_agent.tools.schemas import (
    TOOL_SCHEMA_VERSION,
    RetryPolicy,
    SideEffectClass,
    ToolContract,
)

ANY_OBJECT_SCHEMA = {"type": "object", "additionalProperties": True}
SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {"status": {"type": "string"}},
    "required": ["status"],
}


REGISTERED_TOOLS: dict[str, ToolContract] = {
    "send_message": ToolContract(
        name="send_message",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.SEND,
        idempotency_rule="conversation_id:message_hash:channel",
        timeout_seconds=10,
        retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=1),
        human_gate_rule=(
            "required for pricing, custom commitments, regulated topics, or low confidence"
        ),
    ),
    "create_or_update_lead": ToolContract(
        name="create_or_update_lead",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.WRITE,
        idempotency_rule="source_event_id or lead_id",
        timeout_seconds=10,
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1),
        human_gate_rule="not required when schema validation passes",
    ),
    "lookup_available_slots": ToolContract(
        name="lookup_available_slots",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.READ,
        idempotency_rule=None,
        timeout_seconds=5,
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=0.5),
        human_gate_rule="not required",
    ),
    "book_slot": ToolContract(
        name="book_slot",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.BOOK,
        idempotency_rule="lead_id:slot_id",
        timeout_seconds=10,
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1),
        human_gate_rule="requires explicit customer acceptance and policy eligibility",
    ),
    "lookup_lead_history": ToolContract(
        name="lookup_lead_history",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.READ,
        idempotency_rule=None,
        timeout_seconds=5,
        retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
        human_gate_rule="not required; caller must be tenant-scoped",
    ),
    "create_human_review_task": ToolContract(
        name="create_human_review_task",
        version=TOOL_SCHEMA_VERSION,
        input_schema=ANY_OBJECT_SCHEMA,
        output_schema=SUCCESS_SCHEMA,
        side_effect_class=SideEffectClass.WRITE,
        idempotency_rule="conversation_id:handoff_reason",
        timeout_seconds=5,
        retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=1),
        human_gate_rule="not required; this is the safe fallback",
    ),
}


def get_tool_contract(tool_name: str) -> ToolContract:
    return REGISTERED_TOOLS[tool_name]
