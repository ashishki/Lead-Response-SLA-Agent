"""Async Redis queue helpers."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis


class AsyncRedisQueue:
    """Minimal async queue facade over Redis lists."""

    def __init__(self, client: redis.Redis, queue_name: str) -> None:
        self.client = client
        self.queue_name = queue_name

    async def enqueue(self, payload: dict[str, Any]) -> None:
        await self.client.rpush(self.queue_name, json.dumps(payload, sort_keys=True))

    async def dequeue(self) -> dict[str, Any] | None:
        raw_payload = await self.client.lpop(self.queue_name)
        if raw_payload is None:
            return None

        if isinstance(raw_payload, bytes):
            raw_payload = raw_payload.decode("utf-8")
        return json.loads(raw_payload)
