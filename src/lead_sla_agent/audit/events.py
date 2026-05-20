"""Canonical tenant audit event contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lead_sla_agent.observability.pii import PII_FIELD_NAMES

AUDIT_EVENT_POLICY_VERSION = "audit-policy-v1"
AUDIT_SEARCH_ROLES = frozenset({"owner", "operator"})
SECRET_FIELD_NAMES = frozenset(
    {
        "api_key",
        "authorization",
        "credential",
        "password",
        "secret",
        "token",
    }
)


@dataclass(frozen=True)
class AuditEventInput:
    tenant_id: str
    actor_ref: str
    action: str
    resource_type: str
    resource_id: str
    result: str
    payload: dict[str, Any] = field(default_factory=dict)
    policy_version: str = AUDIT_EVENT_POLICY_VERSION


@dataclass(frozen=True)
class AuditEventRecord:
    tenant_id: str
    actor_ref: str
    action: str
    resource_type: str
    resource_id: str
    result: str
    policy_version: str
    created_at: str
    payload: dict[str, Any]


def validate_audit_event(event: AuditEventInput) -> None:
    if not event.tenant_id:
        raise ValueError("tenant_id is required")
    if not event.actor_ref:
        raise ValueError("actor_ref is required")
    if not event.action:
        raise ValueError("audit action is required")
    if not event.resource_type:
        raise ValueError("audit resource_type is required")
    if not event.resource_id:
        raise ValueError("audit resource_id is required")
    if event.policy_version != AUDIT_EVENT_POLICY_VERSION:
        raise ValueError("unsupported audit policy version")
    rejected = _rejected_payload_paths(event.payload)
    if rejected:
        raise ValueError("audit payload contains PII or secrets: " + ", ".join(sorted(rejected)))


def authorize_audit_search(actor_role: str) -> None:
    if actor_role not in AUDIT_SEARCH_ROLES:
        raise PermissionError("audit search requires owner or operator role")


def _rejected_payload_paths(payload: dict[str, Any]) -> set[str]:
    rejected: set[str] = set()

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, nested_value in value.items():
                nested_path = f"{path}.{key}" if path else key
                key_lower = key.lower()
                if key in PII_FIELD_NAMES or key_lower in SECRET_FIELD_NAMES:
                    rejected.add(nested_path)
                    continue
                visit(nested_value, nested_path)
            return
        if isinstance(value, list):
            for index, nested_value in enumerate(value):
                visit(nested_value, f"{path}[{index}]")
            return
        if isinstance(value, str) and (
            _EMAIL_PATTERN.search(value)
            or _PHONE_PATTERN.search(value)
            or _SECRET_VALUE_PATTERN.search(value)
        ):
            rejected.add(path)

    visit(payload, "")
    return rejected


def isoformat(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_PHONE_PATTERN = re.compile(r"\+?\d[\d .()-]{7,}\d")
_SECRET_VALUE_PATTERN = re.compile(r"(bearer\s+[a-z0-9._-]+|sk-[a-z0-9_-]+)", re.IGNORECASE)
