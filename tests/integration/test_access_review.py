from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from lead_sla_agent.operator.access_review import AccessReviewStore, OperatorAccessRecord
from lead_sla_agent.operator.auth import OperatorPrincipal

NOW = datetime(2026, 5, 23, 12, 0, tzinfo=UTC)


def test_access_review_export_lists_roles_without_pii() -> None:
    store = AccessReviewStore(
        [
            OperatorAccessRecord(
                tenant_id="tenant-1",
                actor_id="owner-1",
                role="owner",
                last_activity_at=NOW - timedelta(days=1),
            ),
            OperatorAccessRecord(
                tenant_id="tenant-1",
                actor_id="operator-1",
                role="operator",
                last_activity_at=NOW - timedelta(hours=2),
            ),
            OperatorAccessRecord(tenant_id="tenant-1", actor_id="viewer-1", role="viewer"),
        ]
    )
    for record in list(store.records.values()):
        store.upsert_account(record)

    report = store.export_access_review(
        tenant_id="tenant-1",
        requested_by=OperatorPrincipal(actor_id="owner-1", tenant_id="tenant-1", role="owner"),
        now=NOW,
    )

    assert report["schema_version"] == "access-review-v1"
    assert len(report["users"]) == 3
    assert all(user["actor_hash"].startswith("sha256:") for user in report["users"])
    serialized = str(report)
    assert "owner-1" not in serialized
    assert "operator-1" not in serialized
    assert "viewer-1" not in serialized
    owner = next(user for user in report["users"] if user["role"] == "owner")
    assert "access_review.export" in owner["privileged_actions"]
    operator = next(user for user in report["users"] if user["role"] == "operator")
    assert "review.approve" in operator["privileged_actions"]


def test_emergency_access_is_time_limited_and_audited() -> None:
    store = _store()

    emergency = store.grant_emergency_access(
        tenant_id="tenant-1",
        actor_id="support-1",
        granted_by=OperatorPrincipal(actor_id="owner-1", tenant_id="tenant-1", role="owner"),
        duration_minutes=30,
        now=NOW,
    )

    assert emergency.role == "emergency_operator"
    assert emergency.emergency_access_expires_at == NOW + timedelta(minutes=30)
    assert store.audit_events[-1]["action"] == "access.emergency.grant"
    store.authorize(
        OperatorPrincipal(actor_id="support-1", tenant_id="tenant-1", role="emergency_operator"),
        "review.approve",
        now=NOW + timedelta(minutes=10),
    )
    with pytest.raises(PermissionError, match="emergency access expired"):
        store.authorize(
            OperatorPrincipal(
                actor_id="support-1",
                tenant_id="tenant-1",
                role="emergency_operator",
            ),
            "review.approve",
            now=NOW + timedelta(minutes=31),
        )


def test_role_downgrade_and_removal_block_privileged_actions_immediately() -> None:
    store = _store()
    owner = OperatorPrincipal(actor_id="owner-1", tenant_id="tenant-1", role="owner")

    store.update_role("tenant-1", "operator-1", "viewer", changed_by=owner, now=NOW)

    with pytest.raises(PermissionError, match="operator role changed"):
        store.authorize(
            OperatorPrincipal(actor_id="operator-1", tenant_id="tenant-1", role="operator"),
            "review.approve",
            now=NOW,
        )
    with pytest.raises(PermissionError, match="operator role is not allowed"):
        store.authorize(
            OperatorPrincipal(actor_id="operator-1", tenant_id="tenant-1", role="viewer"),
            "review.approve",
            now=NOW,
        )

    store.remove_account("tenant-1", "operator-1", removed_by=owner, now=NOW)
    with pytest.raises(PermissionError, match="operator account is not active"):
        store.authorize(
            OperatorPrincipal(actor_id="operator-1", tenant_id="tenant-1", role="viewer"),
            "analytics.read",
            now=NOW,
        )
    assert store.audit_events[-1]["action"] == "operator.remove"


def test_quarterly_access_review_runbook_is_documented() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "Quarterly access review checklist" in content
    assert "Emergency access" in content
    assert "access-review-v1" in content
    assert "Do not include raw names, emails, phone numbers" in content


def _store() -> AccessReviewStore:
    store = AccessReviewStore(
        [
            OperatorAccessRecord(tenant_id="tenant-1", actor_id="owner-1", role="owner"),
            OperatorAccessRecord(tenant_id="tenant-1", actor_id="operator-1", role="operator"),
        ]
    )
    for record in list(store.records.values()):
        store.upsert_account(record)
    return store
