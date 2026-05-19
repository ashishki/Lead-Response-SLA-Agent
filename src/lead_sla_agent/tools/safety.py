"""Unsafe-action gate helpers for tool calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

UNSAFE_MESSAGE_CATEGORIES = frozenset(
    {
        "pricing",
        "custom_commitment",
        "regulated_topic",
        "low_confidence",
        "refund",
    }
)


@dataclass
class HumanReviewQueue:
    tasks: list[dict[str, Any]] = field(default_factory=list)

    async def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.tasks.append(payload)
        return {"status": "queued", "task_id": f"review-{len(self.tasks)}"}


def is_unsafe_message(arguments: dict[str, Any]) -> bool:
    categories = set(arguments.get("unsafe_categories", []))
    return bool(categories & UNSAFE_MESSAGE_CATEGORIES)
