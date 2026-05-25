from __future__ import annotations

from datetime import UTC, datetime

from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.operator.data_admin import TenantDataAdmin, TenantRetentionPolicy


def test_retention_policy_anonymizes_expired_customer_data_and_exports() -> None:
    admin = TenantDataAdmin(
        leads=[
            {
                "tenant_id": "tenant-1",
                "lead_id": "old-lead",
                "contact_name": "Demo Customer",
                "contact_email": "customer@example.test",
                "contact_phone": "+15550101000",
                "created_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "tenant_id": "tenant-1",
                "lead_id": "fresh-lead",
                "contact_name": "Recent Customer",
                "contact_email": "recent@example.test",
                "contact_phone": "+15550102000",
                "created_at": "2026-05-20T00:00:00+00:00",
            },
        ],
        conversations=[
            {
                "tenant_id": "tenant-1",
                "conversation_id": "old-conversation",
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        transcripts=[
            {
                "tenant_id": "tenant-1",
                "message_id": "old-message",
                "provider_message_id": "provider-person-1",
                "redacted_preview": "Private customer message",
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        audit_events=[
            {
                "tenant_id": "tenant-1",
                "event_type": "lead_created",
                "event_metadata": {
                    "email": "customer@example.test",
                    "message": "Private customer message",
                },
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        outcomes=[
            {
                "tenant_id": "tenant-1",
                "lead_id": "old-lead",
                "label": "booked",
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        review_tasks=[
            {
                "tenant_id": "tenant-1",
                "task_id": "old-review",
                "payload": {
                    "email": "customer@example.test",
                    "message": "Private customer message",
                },
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        exports=[
            {
                "tenant_id": "tenant-1",
                "export_id": "old-export",
                "storage_ref": "tenant-1/private-export.json",
                "download_url": "https://example.test/private-export",
                "status": "available",
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    )
    admin.set_retention_policy(
        TenantRetentionPolicy(tenant_id="tenant-1", retain_days=30, mode="anonymize")
    )

    audit = admin.apply_retention_policy(
        tenant_id="tenant-1",
        actor_id="operator-1",
        now=datetime(2026, 5, 23, tzinfo=UTC),
    )
    exported = admin.export_tenant_data("tenant-1")

    assert audit["event_type"] == "tenant_retention_applied"
    assert audit["event_metadata"]["counts"] == {
        "leads": 1,
        "conversations": 1,
        "transcripts": 1,
        "outcomes": 1,
        "review_tasks": 1,
        "audit_events": 1,
        "exports": 1,
    }
    old_lead = next(lead for lead in exported["leads"] if lead["lead_id"] == "old-lead")
    fresh_lead = next(lead for lead in exported["leads"] if lead["lead_id"] == "fresh-lead")
    assert old_lead["contact_name"] == REDACTED_VALUE
    assert old_lead["contact_email"] == REDACTED_VALUE
    assert old_lead["contact_phone"] == REDACTED_VALUE
    assert fresh_lead["contact_name"] == "Recent Customer"
    assert exported["transcripts"][0]["provider_message_id"] is None
    assert exported["review_tasks"][0]["payload"]["email"].startswith("sha256:")
    assert exported["review_tasks"][0]["payload"]["message"] == REDACTED_VALUE
    assert exported["exports"][0]["status"] == "expired"
    assert exported["exports"][0]["storage_ref"] is None
    assert exported["exports"][0]["download_url"] is None
    assert exported["audit_events"][0]["event_metadata"]["email"].startswith("sha256:")
    assert exported["audit_events"][-1]["event_type"] == "tenant_retention_applied"


def test_retention_policy_is_tenant_scoped() -> None:
    admin = TenantDataAdmin(
        leads=[
            {
                "tenant_id": "tenant-1",
                "lead_id": "tenant-1-lead",
                "contact_name": "Tenant One",
                "contact_email": "one@example.test",
                "contact_phone": "+15550101000",
                "created_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "tenant_id": "tenant-2",
                "lead_id": "tenant-2-lead",
                "contact_name": "Tenant Two",
                "contact_email": "two@example.test",
                "contact_phone": "+15550102000",
                "created_at": "2026-01-01T00:00:00+00:00",
            },
        ]
    )
    admin.set_retention_policy(
        TenantRetentionPolicy(tenant_id="tenant-1", retain_days=30, mode="anonymize")
    )

    admin.apply_retention_policy(
        tenant_id="tenant-1",
        actor_id="operator-1",
        now=datetime(2026, 5, 23, tzinfo=UTC),
    )

    tenant_1 = admin.export_tenant_data("tenant-1")["leads"][0]
    tenant_2 = admin.export_tenant_data("tenant-2")["leads"][0]
    assert tenant_1["contact_email"] == REDACTED_VALUE
    assert tenant_2["contact_email"] == "two@example.test"


def test_retention_policy_rejects_unsupported_modes() -> None:
    admin = TenantDataAdmin()
    admin.set_retention_policy(
        TenantRetentionPolicy(tenant_id="tenant-1", retain_days=30, mode="hard_delete")
    )

    try:
        admin.apply_retention_policy(
            tenant_id="tenant-1",
            actor_id="operator-1",
            now=datetime(2026, 5, 23, tzinfo=UTC),
        )
    except ValueError as exc:
        assert str(exc) == "unsupported retention mode"
    else:
        raise AssertionError("unsupported retention mode was accepted")
