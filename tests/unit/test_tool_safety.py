from __future__ import annotations

import pytest

from lead_sla_agent.tools.executor import execute_tool_call
from lead_sla_agent.tools.safety import HumanReviewQueue
from lead_sla_agent.tools.schemas import ToolCall


@pytest.mark.asyncio
async def test_unsafe_message_send_routes_to_human_review() -> None:
    provider_calls: list[ToolCall] = []
    review_queue = HumanReviewQueue()

    async def provider_adapter(tool_call: ToolCall) -> dict[str, str]:
        provider_calls.append(tool_call)
        return {"status": "sent"}

    result = await execute_tool_call(
        ToolCall(
            tool_name="send_message",
            arguments={"text": "Custom price is guaranteed", "unsafe_categories": ["pricing"]},
            idempotency_key="conversation-1:hash:web",
        ),
        provider_adapter,
        review_queue,
    )

    assert result["status"] == "queued"
    assert provider_calls == []
    assert review_queue.tasks[0]["reason"] == "unsafe_message_send"
