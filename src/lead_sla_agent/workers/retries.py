"""Outbound send retry helpers."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

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
