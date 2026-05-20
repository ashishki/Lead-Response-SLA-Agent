"""Human review queue adapter."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.models import HumanReviewApproval, HumanReviewTask
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.observability.tracing import get_tracer


class HumanReviewTaskStore:
    """Human review task store with in-memory and PostgreSQL-backed modes."""

    def __init__(
        self,
        tasks: list[dict[str, Any]] | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self.tasks = tasks if tasks is not None else []
        self.session = session
        self.tracer = get_tracer(__name__)

    async def create_human_review_task(
        self,
        conversation_id: uuid.UUID,
        handoff_reason: str,
        payload: dict[str, Any],
        tenant_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            with self.tracer.start_as_current_span("db.review_task.create"):
                await apply_tenant_context(self.session, tenant_uuid)
                task = HumanReviewTask(
                    tenant_id=tenant_uuid,
                    conversation_id=conversation_id,
                    handoff_reason=handoff_reason,
                    payload=payload,
                    status="open",
                )
                self.session.add(task)
                await _safe_flush(self.session)
            return _task_row(task)

        task = {
            "task_id": "review-" + str(len(self.tasks) + 1),
            "conversation_id": conversation_id,
            "handoff_reason": handoff_reason,
            "payload": payload,
        }
        if tenant_id is not None:
            task["tenant_id"] = str(tenant_id)
        self.tasks.append(task)
        return task

    async def list_tasks(self, tenant_id: str | uuid.UUID) -> list[dict[str, Any]]:
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            statement = (
                select(HumanReviewTask)
                .where(HumanReviewTask.tenant_id == tenant_uuid)
                .order_by(HumanReviewTask.created_at, HumanReviewTask.id)
            )
            with self.tracer.start_as_current_span("db.review_task.list"):
                await apply_tenant_context(self.session, tenant_uuid)
                result = await self.session.execute(statement)
            return [_task_row(task) for task in result.scalars().all()]

        return [task for task in self.tasks if task.get("tenant_id") == str(tenant_id)]

    async def approve_reply(
        self,
        task_id: str,
        actor_id: str,
        original_draft: str,
        final_message: str,
        reason_code: str,
        tenant_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        approved_at = datetime.now(tz=UTC)
        audit_record = {
            "task_id": task_id,
            "actor_id": actor_id,
            "approved_at": approved_at.isoformat(),
            "action_at": approved_at.isoformat(),
            "original_draft_hash": hashlib.sha256(original_draft.encode("utf-8")).hexdigest(),
            "final_message_hash": hashlib.sha256(final_message.encode("utf-8")).hexdigest(),
            "reason_code": reason_code,
            "send_status": "sent",
            "final_status": "sent",
        }
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            review_task_id = uuid.UUID(task_id)
            with self.tracer.start_as_current_span("db.review_approval.create"):
                await apply_tenant_context(self.session, tenant_uuid)
                task = await self.session.get(HumanReviewTask, review_task_id)
                if task is not None:
                    task.status = "sent"
                approval = HumanReviewApproval(
                    tenant_id=tenant_uuid,
                    review_task_id=review_task_id,
                    actor_id=actor_id,
                    approved_at=approved_at,
                    original_draft_hash=audit_record["original_draft_hash"],
                    final_message_hash=audit_record["final_message_hash"],
                    reason_code=reason_code,
                    send_status="sent",
                )
                self.session.add(approval)
                await _safe_flush(self.session)
            return audit_record

        self._mark_memory_task_status(task_id, "sent")
        self.tasks.append({"task_id": "audit-" + str(len(self.tasks) + 1), **audit_record})
        return audit_record

    async def mark_no_send(
        self,
        task_id: str,
        actor_id: str,
        original_draft: str,
        reason_code: str,
        tenant_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        action_at = datetime.now(tz=UTC)
        audit_record = {
            "task_id": task_id,
            "actor_id": actor_id,
            "approved_at": action_at.isoformat(),
            "action_at": action_at.isoformat(),
            "original_draft_hash": hashlib.sha256(original_draft.encode("utf-8")).hexdigest(),
            "final_message_hash": hashlib.sha256(b"").hexdigest(),
            "reason_code": reason_code,
            "send_status": "no_send",
            "final_status": "no_send",
        }
        if self.session is not None:
            tenant_uuid = _require_uuid_tenant_id(tenant_id)
            review_task_id = uuid.UUID(task_id)
            with self.tracer.start_as_current_span("db.review_no_send.create"):
                await apply_tenant_context(self.session, tenant_uuid)
                task = await self.session.get(HumanReviewTask, review_task_id)
                if task is not None:
                    task.status = "no_send"
                approval = HumanReviewApproval(
                    tenant_id=tenant_uuid,
                    review_task_id=review_task_id,
                    actor_id=actor_id,
                    approved_at=action_at,
                    original_draft_hash=audit_record["original_draft_hash"],
                    final_message_hash=audit_record["final_message_hash"],
                    reason_code=reason_code,
                    send_status="no_send",
                )
                self.session.add(approval)
                await _safe_flush(self.session)
            return audit_record

        self._mark_memory_task_status(task_id, "no_send")
        self.tasks.append({"task_id": "audit-" + str(len(self.tasks) + 1), **audit_record})
        return audit_record

    async def get_approval(
        self,
        tenant_id: uuid.UUID | str,
        task_id: str,
    ) -> dict[str, Any] | None:
        if self.session is None:
            return next(
                (task for task in self.tasks if task.get("task_id") == task_id),
                None,
            )

        tenant_uuid = _require_uuid_tenant_id(tenant_id)
        statement = select(HumanReviewApproval).where(
            HumanReviewApproval.tenant_id == tenant_uuid,
            HumanReviewApproval.review_task_id == uuid.UUID(task_id),
        )
        with self.tracer.start_as_current_span("db.review_approval.get"):
            await apply_tenant_context(self.session, tenant_uuid)
            result = await self.session.execute(statement)
            approval = result.scalar_one_or_none()

        if approval is None:
            return None
        return {
            "task_id": str(approval.review_task_id),
            "actor_id": approval.actor_id,
            "approved_at": approval.approved_at.isoformat(),
            "action_at": approval.approved_at.isoformat(),
            "original_draft_hash": approval.original_draft_hash,
            "final_message_hash": approval.final_message_hash,
            "reason_code": approval.reason_code,
            "send_status": approval.send_status,
            "final_status": approval.send_status,
        }

    def _mark_memory_task_status(self, task_id: str, status: str) -> None:
        for task in self.tasks:
            if task.get("task_id") == task_id:
                task["status"] = status
                return


def _require_uuid_tenant_id(tenant_id: uuid.UUID | str | None) -> uuid.UUID:
    if tenant_id is None:
        raise ValueError("tenant_id is required")
    if isinstance(tenant_id, uuid.UUID):
        return tenant_id
    return uuid.UUID(tenant_id)


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise RuntimeError("repository persistence failed") from None


def _task_row(task: HumanReviewTask) -> dict[str, Any]:
    return {
        "task_id": str(task.id),
        "tenant_id": str(task.tenant_id),
        "conversation_id": str(task.conversation_id),
        "handoff_reason": task.handoff_reason,
        "payload": task.payload,
        "status": task.status,
    }
