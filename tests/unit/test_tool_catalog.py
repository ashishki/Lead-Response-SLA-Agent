from __future__ import annotations

import pytest

from lead_sla_agent.tools.catalog import REGISTERED_TOOLS
from lead_sla_agent.tools.executor import ToolExecutionRejected, execute_tool_call
from lead_sla_agent.tools.safety import HumanReviewQueue
from lead_sla_agent.tools.schemas import TOOL_SCHEMA_VERSION, SideEffectClass, ToolCall


def test_registered_tools_expose_contract_fields() -> None:
    assert set(REGISTERED_TOOLS) == {
        "send_message",
        "create_or_update_lead",
        "lookup_available_slots",
        "book_slot",
        "lookup_lead_history",
        "create_human_review_task",
    }
    for tool in REGISTERED_TOOLS.values():
        assert tool.name
        assert tool.version == TOOL_SCHEMA_VERSION
        assert tool.input_schema
        assert tool.output_schema
        assert isinstance(tool.side_effect_class, SideEffectClass)
        assert tool.timeout_seconds > 0
        assert tool.retry_policy.max_attempts >= 1
        assert tool.human_gate_rule


@pytest.mark.asyncio
async def test_write_tools_require_idempotency_key() -> None:
    provider_called = False

    async def provider_adapter(tool_call: ToolCall) -> dict[str, str]:
        nonlocal provider_called
        provider_called = True
        return {"status": "ok"}

    with pytest.raises(ToolExecutionRejected, match="idempotency_key is required"):
        await execute_tool_call(
            ToolCall(tool_name="book_slot", arguments={"lead_id": "lead-1"}),
            provider_adapter,
            HumanReviewQueue(),
        )

    assert provider_called is False
