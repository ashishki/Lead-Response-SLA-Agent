"""Human review queue adapter."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class HumanReviewTaskStore:
    tasks: list[dict[str, Any]] = field(default_factory=list)

    async def create_human_review_task(
        self,
        conversation_id: uuid.UUID,
        handoff_reason: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        task = {
            "task_id": f"review-{len(self.tasks) + 1}",
            "conversation_id": conversation_id,
            "handoff_reason": handoff_reason,
            "payload": payload,
        }
        self.tasks.append(task)
        return task

    async def list_tasks(self, tenant_id: str) -> list[dict[str, Any]]:
        return [task for task in self.tasks if task.get("tenant_id") == tenant_id]

    async def approve_reply(
        self,
        task_id: str,
        actor_id: str,
        original_draft: str,
        final_message: str,
        reason_code: str,
    ) -> dict[str, Any]:
        audit_record = {
            "task_id": task_id,
            "actor_id": actor_id,
            "approved_at": datetime.now(tz=UTC).isoformat(),
            "original_draft_hash": hashlib.sha256(original_draft.encode("utf-8")).hexdigest(),
            "final_message_hash": hashlib.sha256(final_message.encode("utf-8")).hexdigest(),
            "reason_code": reason_code,
            "send_status": "sent",
        }
        self.tasks.append({"task_id": f"audit-{len(self.tasks) + 1}", **audit_record})
        return audit_record
