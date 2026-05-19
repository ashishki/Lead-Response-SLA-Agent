"""Tool call validation and gated execution."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from lead_sla_agent.tools.catalog import get_tool_contract
from lead_sla_agent.tools.safety import HumanReviewQueue, is_unsafe_message
from lead_sla_agent.tools.schemas import ToolCall

ProviderAdapter = Callable[[ToolCall], Awaitable[dict[str, Any]]]


class ToolExecutionRejected(ValueError):
    """Raised when a tool call violates catalog safety rules."""


async def execute_tool_call(
    tool_call: ToolCall,
    provider_adapter: ProviderAdapter,
    review_queue: HumanReviewQueue,
) -> dict[str, Any]:
    contract = get_tool_contract(tool_call.tool_name)
    if contract.requires_idempotency_key and not tool_call.idempotency_key:
        raise ToolExecutionRejected("idempotency_key is required for side-effecting tools")

    if tool_call.tool_name == "send_message" and is_unsafe_message(tool_call.arguments):
        return await review_queue.create_task(
            {
                "reason": "unsafe_message_send",
                "tool_name": tool_call.tool_name,
                "arguments": tool_call.arguments,
                "idempotency_key": tool_call.idempotency_key,
            }
        )

    return await provider_adapter(tool_call)
