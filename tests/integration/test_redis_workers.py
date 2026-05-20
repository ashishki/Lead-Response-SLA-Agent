from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
import redis.asyncio as redis

from lead_sla_agent.workers.retries import get_retry_attempts, record_send_failure_redis
from lead_sla_agent.workers.sla import (
    get_sla_breached_at,
    record_outbound_confirmed,
    record_sla_breach_once,
)

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


@pytest.fixture()
async def redis_client() -> AsyncIterator[redis.Redis]:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    client = redis.from_url(redis_url)
    try:
        await client.ping()
    except Exception as exc:
        await client.aclose()
        pytest.skip("Redis service is not available: " + exc.__class__.__name__)
    await client.flushdb()
    try:
        yield client
    finally:
        await client.flushdb()
        await client.aclose()


@pytest.mark.asyncio
async def test_redis_sla_timer_marks_breach_exactly_once(redis_client: redis.Redis) -> None:
    lead_id = uuid.uuid4()
    now = datetime.now(tz=UTC)
    deadline = now - timedelta(minutes=1)

    assert await record_sla_breach_once(redis_client, TENANT_ID, lead_id, now, deadline) is True
    assert await record_sla_breach_once(redis_client, TENANT_ID, lead_id, now, deadline) is False
    assert await get_sla_breached_at(redis_client, TENANT_ID, lead_id) == int(
        now.timestamp() * 1000
    )


@pytest.mark.asyncio
async def test_redis_sla_timer_ignores_confirmed_outbound(redis_client: redis.Redis) -> None:
    lead_id = uuid.uuid4()
    now = datetime.now(tz=UTC)
    deadline = now - timedelta(minutes=1)

    await record_outbound_confirmed(redis_client, TENANT_ID, lead_id, now - timedelta(minutes=2))

    assert await record_sla_breach_once(redis_client, TENANT_ID, lead_id, now, deadline) is False
    assert await get_sla_breached_at(redis_client, TENANT_ID, lead_id) is None


@pytest.mark.asyncio
async def test_redis_retry_worker_is_idempotent_under_duplicate_delivery(
    redis_client: redis.Redis,
) -> None:
    lead_id = uuid.uuid4()
    review_tasks: list[tuple[uuid.UUID, str]] = []

    async def create_review_task(review_lead_id: uuid.UUID, reason: str) -> None:
        review_tasks.append((review_lead_id, reason))

    assert (
        await record_send_failure_redis(
            redis_client,
            TENANT_ID,
            lead_id,
            "failure-1",
            create_review_task,
            max_attempts=2,
        )
        is False
    )
    assert (
        await record_send_failure_redis(
            redis_client,
            TENANT_ID,
            lead_id,
            "failure-1",
            create_review_task,
            max_attempts=2,
        )
        is False
    )
    assert await get_retry_attempts(redis_client, TENANT_ID, lead_id) == 1

    assert (
        await record_send_failure_redis(
            redis_client,
            TENANT_ID,
            lead_id,
            "failure-2",
            create_review_task,
            max_attempts=2,
        )
        is True
    )
    assert (
        await record_send_failure_redis(
            redis_client,
            TENANT_ID,
            lead_id,
            "failure-3",
            create_review_task,
            max_attempts=2,
        )
        is False
    )
    assert review_tasks == [(lead_id, "outbound_send_retry_exhausted")]
