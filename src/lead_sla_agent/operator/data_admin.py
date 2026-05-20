"""Tenant data export, retention, and anonymization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from lead_sla_agent.audit.events import AUDIT_EVENT_POLICY_VERSION
from lead_sla_agent.observability.pii import REDACTED_VALUE, scrub_pii

EXPORT_SCHEMA_VERSION = "tenant-export-v1"
PII_FIELDS_BY_ENTITY = {
    "leads": ["contact_name", "contact_email", "contact_phone"],
    "transcripts": ["provider_message_id"],
    "audit_events": ["event_metadata"],
    "review_tasks": ["payload"],
}


@dataclass(frozen=True)
class TenantRetentionPolicy:
    tenant_id: str
    retain_days: int
    mode: str = "anonymize"


class TenantDataAdmin:
    def __init__(
        self,
        *,
        leads: list[dict[str, Any]] | None = None,
        conversations: list[dict[str, Any]] | None = None,
        transcripts: list[dict[str, Any]] | None = None,
        audit_events: list[dict[str, Any]] | None = None,
        outcomes: list[dict[str, Any]] | None = None,
        review_tasks: list[dict[str, Any]] | None = None,
    ) -> None:
        self.leads = leads if leads is not None else []
        self.conversations = conversations if conversations is not None else []
        self.transcripts = transcripts if transcripts is not None else []
        self.audit_events = audit_events if audit_events is not None else []
        self.outcomes = outcomes if outcomes is not None else []
        self.review_tasks = review_tasks if review_tasks is not None else []
        self.retention_policies: dict[str, TenantRetentionPolicy] = {}

    def set_retention_policy(self, policy: TenantRetentionPolicy) -> TenantRetentionPolicy:
        self.retention_policies[policy.tenant_id] = policy
        return policy

    def get_retention_policy(self, tenant_id: str) -> TenantRetentionPolicy:
        return self.retention_policies.get(
            tenant_id,
            TenantRetentionPolicy(tenant_id=tenant_id, retain_days=90),
        )

    def export_tenant_data(self, tenant_id: str) -> dict[str, Any]:
        return {
            "schema_version": EXPORT_SCHEMA_VERSION,
            "tenant_id": tenant_id,
            "retention_policy": self.get_retention_policy(tenant_id).__dict__,
            "pii_fields": PII_FIELDS_BY_ENTITY,
            "leads": _filter_tenant_rows(self.leads, tenant_id),
            "conversations": _filter_tenant_rows(self.conversations, tenant_id),
            "transcripts": _filter_tenant_rows(self.transcripts, tenant_id),
            "audit_events": _filter_tenant_rows(self.audit_events, tenant_id),
            "outcomes": _filter_tenant_rows(self.outcomes, tenant_id),
            "review_tasks": _filter_tenant_rows(self.review_tasks, tenant_id),
        }

    def anonymize_tenant_data(
        self,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> dict[str, Any]:
        anonymized_at = datetime.now(tz=UTC).isoformat()
        counts = {
            "leads": _anonymize_rows(self.leads, tenant_id, _anonymize_lead),
            "conversations": _mark_rows_anonymized(self.conversations, tenant_id, anonymized_at),
            "transcripts": _anonymize_rows(self.transcripts, tenant_id, _anonymize_transcript),
            "outcomes": _mark_rows_anonymized(self.outcomes, tenant_id, anonymized_at),
            "review_tasks": _anonymize_rows(self.review_tasks, tenant_id, _anonymize_review_task),
        }
        audit_record = {
            "tenant_id": tenant_id,
            "event_type": "tenant_data_anonymized",
            "actor_type": "operator",
            "actor_id": actor_id,
            "actor_ref": "operator:" + actor_id,
            "action": "tenant_data.anonymized",
            "resource_type": "tenant",
            "resource_id": tenant_id,
            "result": "success",
            "policy_version": AUDIT_EVENT_POLICY_VERSION,
            "created_at": anonymized_at,
            "event_metadata": {
                "reason": reason,
                "retention_policy": self.get_retention_policy(tenant_id).__dict__,
                "counts": counts,
            },
        }
        self.audit_events.append(audit_record)
        return audit_record


def _filter_tenant_rows(rows: list[dict[str, Any]], tenant_id: str) -> list[dict[str, Any]]:
    return [dict(row) for row in rows if row.get("tenant_id") == tenant_id]


def _anonymize_rows(
    rows: list[dict[str, Any]],
    tenant_id: str,
    anonymizer: Any,
) -> int:
    count = 0
    for row in rows:
        if row.get("tenant_id") != tenant_id:
            continue
        anonymizer(row)
        count += 1
    return count


def _mark_rows_anonymized(rows: list[dict[str, Any]], tenant_id: str, anonymized_at: str) -> int:
    count = 0
    for row in rows:
        if row.get("tenant_id") == tenant_id:
            row["anonymized_at"] = anonymized_at
            count += 1
    return count


def _anonymize_lead(row: dict[str, Any]) -> None:
    row["contact_name"] = REDACTED_VALUE
    row["contact_email"] = REDACTED_VALUE
    row["contact_phone"] = REDACTED_VALUE
    row["anonymized_at"] = datetime.now(tz=UTC).isoformat()


def _anonymize_transcript(row: dict[str, Any]) -> None:
    row["provider_message_id"] = None
    row["redacted_preview"] = REDACTED_VALUE
    row["anonymized_at"] = datetime.now(tz=UTC).isoformat()


def _anonymize_review_task(row: dict[str, Any]) -> None:
    row["payload"] = scrub_pii(row.get("payload", {}))
    row["anonymized_at"] = datetime.now(tz=UTC).isoformat()
