"""Production access review and emergency access controls."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from lead_sla_agent.audit.events import AUDIT_EVENT_POLICY_VERSION
from lead_sla_agent.operator.auth import OperatorPrincipal

OWNER_ACTIONS = frozenset(
    {
        "access_review.export",
        "access.emergency.grant",
        "access.emergency.revoke",
        "tenant_config.dangerous_update",
        "operator.remove",
        "operator.role_update",
    }
)
OPERATOR_ACTIONS = frozenset(
    {
        "review.approve",
        "review.no_send",
        "outcome.label",
        "analytics.read",
        "knowledge.reindex",
    }
)
VIEWER_ACTIONS = frozenset({"analytics.read"})
ROLE_ACTIONS = {
    "owner": OWNER_ACTIONS | OPERATOR_ACTIONS | VIEWER_ACTIONS,
    "operator": OPERATOR_ACTIONS | VIEWER_ACTIONS,
    "viewer": VIEWER_ACTIONS,
    "emergency_operator": OPERATOR_ACTIONS | VIEWER_ACTIONS,
}
ACTIVE_STATUSES = frozenset({"active", "emergency"})


@dataclass
class OperatorAccessRecord:
    tenant_id: str
    actor_id: str
    role: str
    status: str = "active"
    last_activity_at: datetime | None = None
    emergency_access_expires_at: datetime | None = None
    granted_by_hash: str | None = None
    privileged_actions: tuple[str, ...] = field(default_factory=tuple)


class AccessReviewStore:
    def __init__(self, records: list[OperatorAccessRecord] | None = None) -> None:
        self.records: dict[tuple[str, str], OperatorAccessRecord] = {}
        self.audit_events: list[dict[str, Any]] = []
        for record in records or []:
            self.records[(record.tenant_id, record.actor_id)] = record

    def upsert_account(self, record: OperatorAccessRecord) -> OperatorAccessRecord:
        if not record.privileged_actions:
            record.privileged_actions = tuple(sorted(ROLE_ACTIONS.get(record.role, frozenset())))
        self.records[(record.tenant_id, record.actor_id)] = record
        return record

    def export_access_review(
        self,
        tenant_id: str,
        requested_by: OperatorPrincipal,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        self.authorize(requested_by, "access_review.export", now=now)
        users = [
            _export_record(record, now or datetime.now(tz=UTC))
            for record in self.records.values()
            if record.tenant_id == tenant_id
        ]
        return {
            "schema_version": "access-review-v1",
            "tenant_id": tenant_id,
            "generated_at": (now or datetime.now(tz=UTC)).isoformat(),
            "generated_by_hash": _hash_ref(requested_by.actor_id),
            "users": sorted(users, key=lambda user: user["actor_hash"]),
        }

    def authorize(
        self,
        principal: OperatorPrincipal,
        action: str,
        now: datetime | None = None,
    ) -> None:
        record = self.records.get((principal.tenant_id, principal.actor_id))
        if record is None:
            raise PermissionError("operator account is not active")
        current_time = now or datetime.now(tz=UTC)
        if record.status not in ACTIVE_STATUSES:
            raise PermissionError("operator account is not active")
        if record.role == "emergency_operator":
            expires_at = record.emergency_access_expires_at
            if expires_at is None or expires_at <= current_time:
                raise PermissionError("emergency access expired")
        if principal.role != record.role:
            raise PermissionError("operator role changed")
        if action not in ROLE_ACTIONS.get(record.role, frozenset()):
            raise PermissionError("operator role is not allowed for action")
        record.last_activity_at = current_time

    def update_role(
        self,
        tenant_id: str,
        actor_id: str,
        role: str,
        changed_by: OperatorPrincipal,
        now: datetime | None = None,
    ) -> OperatorAccessRecord:
        self.authorize(changed_by, "operator.role_update", now=now)
        record = self._require_record(tenant_id, actor_id)
        record.role = role
        record.status = "active"
        record.emergency_access_expires_at = None
        record.granted_by_hash = None
        record.privileged_actions = tuple(sorted(ROLE_ACTIONS.get(role, frozenset())))
        self._append_audit(
            tenant_id=tenant_id,
            actor_id=changed_by.actor_id,
            action="operator.role_update",
            resource_id=actor_id,
            now=now,
            metadata={"target_actor_hash": _hash_ref(actor_id), "new_role": role},
        )
        return record

    def remove_account(
        self,
        tenant_id: str,
        actor_id: str,
        removed_by: OperatorPrincipal,
        now: datetime | None = None,
    ) -> OperatorAccessRecord:
        self.authorize(removed_by, "operator.remove", now=now)
        record = self._require_record(tenant_id, actor_id)
        record.status = "removed"
        record.privileged_actions = ()
        record.emergency_access_expires_at = None
        self._append_audit(
            tenant_id=tenant_id,
            actor_id=removed_by.actor_id,
            action="operator.remove",
            resource_id=actor_id,
            now=now,
            metadata={"target_actor_hash": _hash_ref(actor_id)},
        )
        return record

    def grant_emergency_access(
        self,
        tenant_id: str,
        actor_id: str,
        granted_by: OperatorPrincipal,
        duration_minutes: int,
        now: datetime | None = None,
    ) -> OperatorAccessRecord:
        self.authorize(granted_by, "access.emergency.grant", now=now)
        if duration_minutes <= 0 or duration_minutes > 240:
            raise ValueError("emergency access duration must be 1-240 minutes")
        current_time = now or datetime.now(tz=UTC)
        record = self.records.get((tenant_id, actor_id)) or OperatorAccessRecord(
            tenant_id=tenant_id,
            actor_id=actor_id,
            role="emergency_operator",
        )
        record.role = "emergency_operator"
        record.status = "emergency"
        record.emergency_access_expires_at = current_time + timedelta(minutes=duration_minutes)
        record.granted_by_hash = _hash_ref(granted_by.actor_id)
        record.privileged_actions = tuple(sorted(ROLE_ACTIONS["emergency_operator"]))
        self.records[(tenant_id, actor_id)] = record
        self._append_audit(
            tenant_id=tenant_id,
            actor_id=granted_by.actor_id,
            action="access.emergency.grant",
            resource_id=actor_id,
            now=current_time,
            metadata={
                "target_actor_hash": _hash_ref(actor_id),
                "expires_at": record.emergency_access_expires_at.isoformat(),
            },
        )
        return record

    def _require_record(self, tenant_id: str, actor_id: str) -> OperatorAccessRecord:
        record = self.records.get((tenant_id, actor_id))
        if record is None:
            raise PermissionError("operator account is not active")
        return record

    def _append_audit(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        action: str,
        resource_id: str,
        metadata: dict[str, Any],
        now: datetime | None = None,
    ) -> None:
        created_at = now or datetime.now(tz=UTC)
        self.audit_events.append(
            {
                "tenant_id": tenant_id,
                "event_type": action.replace(".", "_"),
                "actor_ref": "operator:" + _hash_ref(actor_id),
                "action": action,
                "resource_type": "operator_access",
                "resource_ref": _hash_ref(resource_id),
                "result": "success",
                "policy_version": AUDIT_EVENT_POLICY_VERSION,
                "created_at": created_at.isoformat(),
                "event_metadata": metadata,
            }
        )


def _export_record(record: OperatorAccessRecord, now: datetime) -> dict[str, Any]:
    emergency_active = (
        record.role == "emergency_operator"
        and record.emergency_access_expires_at is not None
        and record.emergency_access_expires_at > now
    )
    return {
        "actor_hash": _hash_ref(record.actor_id),
        "role": record.role,
        "status": record.status,
        "last_activity_at": record.last_activity_at.isoformat()
        if record.last_activity_at
        else None,
        "privileged_actions": list(record.privileged_actions),
        "emergency_access_expires_at": record.emergency_access_expires_at.isoformat()
        if record.emergency_access_expires_at
        else None,
        "emergency_access_active": emergency_active,
        "granted_by_hash": record.granted_by_hash,
    }


def _hash_ref(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()
