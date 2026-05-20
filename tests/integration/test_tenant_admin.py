from __future__ import annotations

import pytest

from lead_sla_agent.operator.tenant_admin import TenantAdminStore


def test_tenant_admin_updates_safe_configuration_without_deployment() -> None:
    store = TenantAdminStore()

    updated = store.update_config(
        tenant_id="tenant-1",
        actor_id="operator-1",
        actor_role="operator",
        changes={
            "channels": ["website_form", "sms"],
            "business_hours": {
                "timezone": "America/Chicago",
                "days": ["mon-sat"],
                "hours": "07-19",
            },
            "required_fields": ["customer_name", "phone", "door_issue", "urgency"],
            "max_turns": 5,
            "provider_settings": {"outbound_channel": "sms"},
        },
    )

    assert updated.version == 2
    assert updated.config["channels"] == ["website_form", "sms"]
    assert updated.config["max_turns"] == 5
    assert store.history("tenant-1")[0]["event_metadata"]["dangerous_change"] is False


def test_dangerous_policy_change_requires_owner_or_approval() -> None:
    store = TenantAdminStore()

    with pytest.raises(
        PermissionError,
        match="dangerous tenant config changes require owner role or approval",
    ):
        store.update_config(
            tenant_id="tenant-1",
            actor_id="operator-1",
            actor_role="operator",
            changes={"autonomous_send_enabled": False},
        )

    owner_update = store.update_config(
        tenant_id="tenant-1",
        actor_id="owner-1",
        actor_role="owner",
        changes={"handoff_policy": ["unsupported_question", "high_value_lead"]},
    )
    approved_update = store.update_config(
        tenant_id="tenant-1",
        actor_id="operator-1",
        actor_role="operator",
        changes={"unsafe_categories": ["pricing_commitment", "complaint_or_refund"]},
        approval_id="approval-1",
    )

    assert owner_update.version == 2
    assert approved_update.version == 3
    assert [event["event_metadata"]["dangerous_change"] for event in store.history("tenant-1")] == [
        True,
        True,
    ]
    assert store.history("tenant-1")[-1]["event_metadata"]["approval_id"] == "approval-1"


def test_tenant_admin_rejects_unknown_config_fields() -> None:
    store = TenantAdminStore()

    with pytest.raises(ValueError, match="unsupported tenant config fields"):
        store.update_config(
            tenant_id="tenant-1",
            actor_id="operator-1",
            actor_role="operator",
            changes={"raw_prompt_override": "unsafe"},
        )


def test_tenant_config_history_is_tenant_scoped_and_versioned() -> None:
    store = TenantAdminStore()

    first = store.update_config(
        tenant_id="tenant-1",
        actor_id="operator-1",
        actor_role="operator",
        changes={"max_turns": 4},
    )
    second = store.update_config(
        tenant_id="tenant-2",
        actor_id="operator-2",
        actor_role="operator",
        changes={"max_turns": 3},
    )

    assert first.version == 2
    assert second.version == 2
    assert [event["tenant_id"] for event in store.history("tenant-1")] == ["tenant-1"]
    assert store.history("tenant-1")[0]["event_metadata"] == {
        "changed_fields": ["max_turns"],
        "previous_version": 1,
        "new_version": 2,
        "approval_id": None,
        "dangerous_change": False,
    }
