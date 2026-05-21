"""Outbound send retry helpers."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from redis.asyncio import Redis

from lead_sla_agent.observability.metrics import metrics
from lead_sla_agent.tools.messaging import MessageSendResult

CreateReviewTask = Callable[[uuid.UUID, str], Awaitable[None]]


@dataclass
class RetryState:
    lead_id: uuid.UUID
    attempts: int = 0
    max_attempts: int = 3
    human_review_created: bool = False


async def record_send_failure(
    retry_state: RetryState,
    create_review_task: CreateReviewTask,
    reason: str = "outbound_send_retry_exhausted",
) -> bool:
    """Record a failed send and create one human-review task after retry exhaustion."""
    if retry_state.human_review_created:
        return False

    retry_state.attempts += 1
    if retry_state.attempts < retry_state.max_attempts:
        return False

    await create_review_task(retry_state.lead_id, reason)
    retry_state.human_review_created = True
    return True


async def record_provider_send_result(
    retry_state: RetryState,
    result: MessageSendResult,
    create_review_task: CreateReviewTask,
) -> bool:
    """Route failed provider sends into retry/handoff metrics without duplicating sends."""
    if result.status not in {"failed", "rate_limited"}:
        return False
    if retry_state.human_review_created:
        return False

    metrics.increment("provider_send_failure_total")
    reason = (
        "provider_rate_limited"
        if result.rate_limited
        else (result.failure_reason or "provider_send_failed")
    )
    return await record_send_failure(
        retry_state=retry_state,
        create_review_task=create_review_task,
        reason=reason,
    )


async def record_send_failure_redis(
    client: Redis,
    tenant_id: uuid.UUID,
    lead_id: uuid.UUID,
    failure_event_id: str,
    create_review_task: CreateReviewTask,
    max_attempts: int = 3,
    reason: str = "outbound_send_retry_exhausted",
) -> bool:
    """Record one Redis-backed send failure and create one review after exhaustion."""
    processed = await client.set(
        _retry_event_key(tenant_id, lead_id, failure_event_id),
        "1",
        nx=True,
    )
    if not processed:
        return False

    state_key = _retry_state_key(tenant_id, lead_id)
    attempts = await client.hincrby(state_key, "attempts", 1)
    await client.hset(state_key, "max_attempts", max_attempts)
    if attempts < max_attempts:
        return False

    review_created = await client.set(_retry_review_key(tenant_id, lead_id), "1", nx=True)
    if not review_created:
        return False

    await create_review_task(lead_id, reason)
    await client.hset(state_key, mapping={"human_review_created": "1", "reason": reason})
    return True


async def get_retry_attempts(client: Redis, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> int:
    """Return the Redis-backed retry attempt count for tests and workers."""
    value = await client.hget(_retry_state_key(tenant_id, lead_id), "attempts")
    if value is None:
        return 0
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return int(value)


def _retry_state_key(tenant_id: uuid.UUID, lead_id: uuid.UUID) -> str:
    return "retry:state:" + str(tenant_id) + ":" + str(lead_id)


def _retry_event_key(tenant_id: uuid.UUID, lead_id: uuid.UUID, failure_event_id: str) -> str:
    return "retry:event:" + str(tenant_id) + ":" + str(lead_id) + ":" + failure_event_id


def _retry_review_key(tenant_id: uuid.UUID, lead_id: uuid.UUID) -> str:
    return "retry:review:" + str(tenant_id) + ":" + str(lead_id)
