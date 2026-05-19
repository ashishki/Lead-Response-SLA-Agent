from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from lead_sla_agent.workers.retries import RetryState, record_send_failure
from lead_sla_agent.workers.sla import LeadSLAState, record_sla_breach_if_needed


def test_sla_timer_records_breach() -> None:
    now = datetime.now(tz=UTC)
    lead = LeadSLAState(lead_id=uuid.uuid4(), created_at=now - timedelta(minutes=10))
    deadline = now - timedelta(minutes=5)

    assert record_sla_breach_if_needed(lead, now=now, response_deadline=deadline) is True
    assert lead.sla_breached_at == now

    assert record_sla_breach_if_needed(lead, now=now, response_deadline=deadline) is False


@pytest.mark.asyncio
async def test_retry_exhaustion_creates_review_task() -> None:
    review_tasks: list[tuple[uuid.UUID, str]] = []
    retry_state = RetryState(lead_id=uuid.uuid4(), max_attempts=2)

    async def create_review_task(lead_id: uuid.UUID, reason: str) -> None:
        review_tasks.append((lead_id, reason))

    assert await record_send_failure(retry_state, create_review_task) is False
    assert await record_send_failure(retry_state, create_review_task) is True
    assert await record_send_failure(retry_state, create_review_task) is False

    assert review_tasks == [(retry_state.lead_id, "outbound_send_retry_exhausted")]
