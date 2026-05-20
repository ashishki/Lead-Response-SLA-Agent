from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from lead_sla_agent.verticals import load_vertical_pack
from scripts.onboard_tenant import (
    build_onboarding_plan,
    load_onboarding_questions,
    validate_knowledge_questions,
)


def test_onboarding_checklist_initializes_tenant_under_one_working_day() -> None:
    plan = build_onboarding_plan(
        tenant_name="DFW Door Pilot",
        tenant_slug="dfw-door-pilot",
        vertical_slug="garage_door_repair",
        operator_email="operator@example.test",
    )

    assert plan["schema_version"] == "tenant-onboarding-v1"
    assert plan["tenant"]["slug"] == "dfw-door-pilot"
    assert plan["tenant"]["operator_email_hash"].startswith("sha256:")
    assert plan["estimated_hours"] <= 8
    assert plan["fits_in_one_working_day"] is True
    assert {item["step"] for item in plan["checklist"]} >= {
        "tenant_creation",
        "provider_connection",
        "knowledge_upload",
        "operator_accounts",
        "knowledge_validation",
        "operator_approval_test",
        "test_lead_validation",
    }


def test_onboarding_provider_sandbox_event_sends_and_receives() -> None:
    plan = build_onboarding_plan(
        tenant_name="DFW Door Pilot",
        tenant_slug="dfw-door-pilot",
        vertical_slug="garage_door_repair",
        operator_email="operator@example.test",
    )
    sandbox = plan["provider_sandbox"]

    assert sandbox["provider"] == "sandbox"
    assert sandbox["sent"] is True
    assert sandbox["received"] is True
    assert sandbox["payload_hash"]
    assert sandbox["passed"] is True


def test_onboarding_knowledge_validation_checks_at_least_ten_questions() -> None:
    pack = load_vertical_pack("garage_door_repair")
    questions = load_onboarding_questions("garage_door_repair")
    validation = validate_knowledge_questions(pack, questions)

    assert validation["question_count"] >= 10
    assert validation["source_document_count"] >= 5
    assert validation["missing_source_question_ids"] == []
    assert validation["passed"] is True


def test_onboarding_operator_approval_path_is_tested() -> None:
    plan = build_onboarding_plan(
        tenant_name="DFW Door Pilot",
        tenant_slug="dfw-door-pilot",
        vertical_slug="garage_door_repair",
        operator_email="operator@example.test",
    )

    assert plan["operator_approval_path"]["task_id"] == "onboarding-review-1"
    assert plan["operator_approval_path"]["actor_id"] == "onboarding-operator"
    assert plan["operator_approval_path"]["reason_code"] == "onboarding_test_approval"
    assert plan["operator_approval_path"]["final_status"] == "sent"
    assert plan["operator_approval_path"]["passed"] is True


def test_onboarding_cli_outputs_json_plan() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/onboard_tenant.py",
            "--tenant-name",
            "DFW Door Pilot",
            "--tenant-slug",
            "dfw-door-pilot",
            "--operator-email",
            "operator@example.test",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["tenant"]["vertical_slug"] == "garage_door_repair"
    assert payload["knowledge_validation"]["passed"] is True
    assert payload["provider_sandbox"]["passed"] is True
