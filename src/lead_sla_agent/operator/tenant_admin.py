"""Tenant configuration admin with versioned audit records."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

SAFE_CONFIG_FIELDS = frozenset(
    {
        "channels",
        "business_hours",
        "required_fields",
        "max_turns",
        "provider_settings",
    }
)
DANGEROUS_CONFIG_FIELDS = frozenset(
    {
        "handoff_policy",
        "unsafe_categories",
        "autonomous_send_enabled",
    }
)
ELEVATED_ROLES = frozenset({"owner"})


@dataclass(frozen=True)
class TenantConfigRecord:
    tenant_id: str
    version: int
    config: dict[str, Any]
    updated_at: str


@dataclass(frozen=True)
class TenantConfigChange:
    tenant_id: str
    actor_id: str
    actor_role: str
    changed_fields: list[str]
    previous_version: int
    new_version: int
    approval_id: str | None
    changed_at: str


@dataclass
class TenantAdminStore:
    configs: dict[str, TenantConfigRecord] = field(default_factory=dict)
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def get_config(self, tenant_id: str) -> TenantConfigRecord:
        existing = self.configs.get(tenant_id)
        if existing is not None:
            return existing

        created = TenantConfigRecord(
            tenant_id=tenant_id,
            version=1,
            config=_default_config(),
            updated_at=datetime.now(tz=UTC).isoformat(),
        )
        self.configs[tenant_id] = created
        return created

    def update_config(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        actor_role: str,
        changes: dict[str, Any],
        approval_id: str | None = None,
    ) -> TenantConfigRecord:
        changed_fields = sorted(changes)
        unknown_fields = set(changed_fields) - SAFE_CONFIG_FIELDS - DANGEROUS_CONFIG_FIELDS
        if unknown_fields:
            raise ValueError(
                "unsupported tenant config fields: " + ", ".join(sorted(unknown_fields))
            )

        dangerous_fields = set(changed_fields) & DANGEROUS_CONFIG_FIELDS
        if dangerous_fields and actor_role not in ELEVATED_ROLES and approval_id is None:
            raise PermissionError("dangerous tenant config changes require owner role or approval")

        previous = self.get_config(tenant_id)
        next_config = deepcopy(previous.config)
        for field_name, value in changes.items():
            next_config[field_name] = value

        updated = TenantConfigRecord(
            tenant_id=tenant_id,
            version=previous.version + 1,
            config=next_config,
            updated_at=datetime.now(tz=UTC).isoformat(),
        )
        self.configs[tenant_id] = updated
        self._audit_change(
            TenantConfigChange(
                tenant_id=tenant_id,
                actor_id=actor_id,
                actor_role=actor_role,
                changed_fields=changed_fields,
                previous_version=previous.version,
                new_version=updated.version,
                approval_id=approval_id,
                changed_at=updated.updated_at,
            )
        )
        return updated

    def history(self, tenant_id: str) -> list[dict[str, Any]]:
        return [event for event in self.audit_events if event["tenant_id"] == tenant_id]

    def _audit_change(self, change: TenantConfigChange) -> None:
        self.audit_events.append(
            {
                "tenant_id": change.tenant_id,
                "event_type": "tenant_config_updated",
                "actor_id": change.actor_id,
                "actor_role": change.actor_role,
                "created_at": change.changed_at,
                "event_metadata": {
                    "changed_fields": change.changed_fields,
                    "previous_version": change.previous_version,
                    "new_version": change.new_version,
                    "approval_id": change.approval_id,
                    "dangerous_change": bool(set(change.changed_fields) & DANGEROUS_CONFIG_FIELDS),
                },
            }
        )


def _default_config() -> dict[str, Any]:
    return {
        "channels": ["website_form"],
        "business_hours": {"timezone": "America/Chicago", "days": ["mon-fri"], "hours": "08-18"},
        "required_fields": ["customer_name", "phone", "service_address_or_zip", "door_issue"],
        "max_turns": 6,
        "provider_settings": {"outbound_channel": "email"},
        "handoff_policy": ["unsupported_question", "booking_without_acceptance"],
        "unsafe_categories": ["pricing_commitment", "regulated_or_safety_advice"],
        "autonomous_send_enabled": True,
    }
