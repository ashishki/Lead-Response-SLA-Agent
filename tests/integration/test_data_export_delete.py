from __future__ import annotations

from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.operator.data_admin import (
    EXPORT_SCHEMA_VERSION,
    TenantDataAdmin,
    TenantRetentionPolicy,
)


def test_tenant_export_includes_all_privacy_sections_and_pii_schema() -> None:
    admin = _admin()
    admin.set_retention_policy(
        TenantRetentionPolicy(tenant_id="tenant-1", retain_days=30, mode="anonymize")
    )

    exported = admin.export_tenant_data("tenant-1")

    assert exported["schema_version"] == EXPORT_SCHEMA_VERSION
    assert exported["tenant_id"] == "tenant-1"
    assert exported["retention_policy"]["retain_days"] == 30
    assert exported["pii_fields"]["leads"] == [
        "contact_name",
        "contact_email",
        "contact_phone",
    ]
    assert exported["leads"] == [
        {
            "tenant_id": "tenant-1",
            "lead_id": "lead-1",
            "contact_name": "Demo Customer",
            "contact_email": "customer@example.test",
            "contact_phone": "+15550101000",
        }
    ]
    assert len(exported["conversations"]) == 1
    assert len(exported["transcripts"]) == 1
    assert len(exported["audit_events"]) == 1
    assert len(exported["outcomes"]) == 1
    assert len(exported["review_tasks"]) == 1


def test_tenant_export_is_tenant_scoped() -> None:
    exported = _admin().export_tenant_data("tenant-2")

    assert [lead["lead_id"] for lead in exported["leads"]] == ["lead-2"]
    assert exported["conversations"] == []
    assert exported["transcripts"] == []
    assert exported["audit_events"] == []
    assert exported["outcomes"] == []
    assert exported["review_tasks"] == []


def test_anonymize_tenant_data_redacts_pii_and_records_audit() -> None:
    admin = _admin()

    audit_record = admin.anonymize_tenant_data(
        tenant_id="tenant-1",
        actor_id="operator-1",
        reason="customer_delete_request",
    )
    exported = admin.export_tenant_data("tenant-1")

    assert audit_record["event_type"] == "tenant_data_anonymized"
    assert audit_record["actor_id"] == "operator-1"
    assert audit_record["event_metadata"]["reason"] == "customer_delete_request"
    assert audit_record["event_metadata"]["counts"]["leads"] == 1
    assert exported["leads"][0]["contact_name"] == REDACTED_VALUE
    assert exported["leads"][0]["contact_email"] == REDACTED_VALUE
    assert exported["leads"][0]["contact_phone"] == REDACTED_VALUE
    assert exported["transcripts"][0]["provider_message_id"] is None
    assert exported["review_tasks"][0]["payload"]["email"].startswith("sha256:")
    assert exported["review_tasks"][0]["payload"]["message"] == REDACTED_VALUE
    assert exported["audit_events"][-1]["event_type"] == "tenant_data_anonymized"


def test_retention_policy_is_configurable_per_tenant() -> None:
    admin = TenantDataAdmin()

    default_policy = admin.get_retention_policy("tenant-1")
    updated_policy = admin.set_retention_policy(
        TenantRetentionPolicy(tenant_id="tenant-1", retain_days=45, mode="anonymize")
    )

    assert default_policy.retain_days == 90
    assert updated_policy.retain_days == 45
    assert admin.get_retention_policy("tenant-1").retain_days == 45


def _admin() -> TenantDataAdmin:
    return TenantDataAdmin(
        leads=[
            {
                "tenant_id": "tenant-1",
                "lead_id": "lead-1",
                "contact_name": "Demo Customer",
                "contact_email": "customer@example.test",
                "contact_phone": "+15550101000",
            },
            {
                "tenant_id": "tenant-2",
                "lead_id": "lead-2",
                "contact_name": "Other Customer",
                "contact_email": "other@example.test",
                "contact_phone": "+15550102000",
            },
        ],
        conversations=[{"tenant_id": "tenant-1", "conversation_id": "conversation-1"}],
        transcripts=[
            {
                "tenant_id": "tenant-1",
                "message_id": "message-1",
                "provider_message_id": "provider-message-1",
                "redacted_preview": "[redacted]",
            }
        ],
        audit_events=[
            {
                "tenant_id": "tenant-1",
                "event_type": "lead_created",
                "event_metadata": {"lead_id": "lead-1"},
            }
        ],
        outcomes=[{"tenant_id": "tenant-1", "lead_id": "lead-1", "label": "booked"}],
        review_tasks=[
            {
                "tenant_id": "tenant-1",
                "task_id": "review-1",
                "payload": {
                    "email": "customer@example.test",
                    "message": "Private customer details",
                    "evidence_ids": ["gd-pricing-ranges"],
                },
            }
        ],
    )
