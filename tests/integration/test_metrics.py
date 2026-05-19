from __future__ import annotations

import pytest

from lead_sla_agent.observability.metrics import metrics
from tests.integration.test_end_to_end_workflow import inbound_event, workflow


@pytest.mark.asyncio
async def test_workflow_emits_required_metrics() -> None:
    metrics.reset()

    await (await workflow()).process_inbound_event(
        inbound_event("Are same-day appointments available?"),
        asks_policy_question=True,
    )

    assert metrics.histograms["first_response_latency_ms"]
    assert metrics.counters["sla_processed_total"] == 1
    assert metrics.histograms["retrieval_latency_ms"] == [0]
    assert metrics.counters["tool_call_success_total"] == 1
    assert metrics.counters["agent_termination_reason_responded_total"] == 1
