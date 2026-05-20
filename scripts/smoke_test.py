"""Post-deploy smoke checks for staging and production."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from lead_sla_agent.operator.auth import issue_operator_token
from lead_sla_agent.tools.executor import execute_tool_call
from lead_sla_agent.tools.messaging import FakeMessagingAdapter
from lead_sla_agent.tools.safety import HumanReviewQueue
from lead_sla_agent.tools.schemas import ToolCall


class HTTPClient(Protocol):
    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""


@dataclass(frozen=True)
class SmokeConfig:
    environment: str
    base_url: str
    tenant_id: str
    sandbox_mode: bool = False
    database_url: str | None = None
    redis_url: str | None = None


async def run_smoke_checks(
    config: SmokeConfig,
    client: HTTPClient | None = None,
) -> dict[str, Any]:
    owns_client = client is None
    http_client = client or httpx.AsyncClient(base_url=config.base_url, timeout=10)
    try:
        health = await check_api_health(http_client)
        migration_version = await check_migration_version(config.database_url)
        redis_status = await check_redis(config.redis_url)
        operator_auth = await check_operator_auth(http_client, config.tenant_id)
        provider_sandbox = await check_provider_sandbox(config.sandbox_mode)
        safe_handoff = await check_safe_handoff()
    finally:
        if owns_client:
            await http_client.aclose()  # type: ignore[attr-defined]

    return {
        "environment": config.environment,
        "status": "ok",
        "checks": {
            "health": health,
            "migration_version": migration_version,
            "redis": redis_status,
            "operator_auth": operator_auth,
            "provider_sandbox": provider_sandbox,
            "safe_handoff": safe_handoff,
        },
    }


async def check_api_health(client: HTTPClient) -> str:
    response = await client.get("/health")
    response.raise_for_status()
    body = response.json()
    if body.get("status") != "ok":
        raise RuntimeError("health check failed")
    return "ok"


async def check_migration_version(database_url: str | None) -> str:
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for smoke migration check")

    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar_one_or_none()
    finally:
        await engine.dispose()
    if not version:
        raise RuntimeError("alembic migration version is missing")
    return str(version)


async def check_redis(redis_url: str | None) -> str:
    if not redis_url:
        raise RuntimeError("REDIS_URL is required for smoke Redis check")

    client = redis.from_url(redis_url)
    try:
        pong = await client.ping()
    finally:
        await client.aclose()
    if pong is not True:
        raise RuntimeError("redis ping failed")
    return "ok"


async def check_operator_auth(client: HTTPClient, tenant_id: str) -> str:
    token = issue_operator_token("smoke-operator", tenant_id, "operator")
    response = await client.get("/operator/reviews", headers={"authorization": f"Bearer {token}"})
    response.raise_for_status()
    if "tasks" not in response.json():
        raise RuntimeError("operator auth smoke failed")
    return "ok"


async def check_provider_sandbox(sandbox_mode: bool) -> str:
    if not sandbox_mode:
        return "skipped"

    result = await FakeMessagingAdapter().send_message(
        channel="email",
        recipient="sandbox@example.test",
        text="sandbox smoke test",
        idempotency_key="smoke:sandbox:message",
    )
    if result.status != "sent":
        raise RuntimeError("provider sandbox smoke failed")
    return "ok"


async def check_safe_handoff() -> str:
    provider_called = False
    review_queue = HumanReviewQueue()

    async def provider_adapter(tool_call: ToolCall) -> dict[str, str]:
        nonlocal provider_called
        provider_called = True
        return {"status": "sent"}

    result = await execute_tool_call(
        ToolCall(
            tool_name="send_message",
            arguments={"text": "Custom price is guaranteed", "unsafe_categories": ["pricing"]},
            idempotency_key="smoke:safe-handoff",
        ),
        provider_adapter,
        review_queue,
    )
    if provider_called or result.get("status") != "queued":
        raise RuntimeError("safe handoff smoke failed")
    return "ok"


def parse_args() -> SmokeConfig:
    parser = argparse.ArgumentParser(description="Run post-deploy smoke checks.")
    parser.add_argument("--environment", choices=("staging", "production"), required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--sandbox-mode", action="store_true")
    args = parser.parse_args()
    return SmokeConfig(
        environment=args.environment,
        base_url=args.base_url,
        tenant_id=args.tenant_id,
        sandbox_mode=args.sandbox_mode,
        database_url=os.environ.get("DATABASE_URL"),
        redis_url=os.environ.get("REDIS_URL"),
    )


async def main() -> None:
    result = await run_smoke_checks(parse_args())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
