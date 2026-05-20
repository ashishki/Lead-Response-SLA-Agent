from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from scripts.reset_demo_tenant import build_demo_state, reset_demo_tenant


def test_demo_tenant_contains_required_sales_scenarios() -> None:
    state = build_demo_state()
    lead_scenarios = {lead["scenario"] for lead in state["leads"]}
    review_scenarios = {task["scenario"] for task in state["review_tasks"]}

    assert state["schema_version"] == "demo-tenant-state-v1"
    assert lead_scenarios >= {
        "supported_faq",
        "unsupported_handoff",
        "booking_proposal",
    }
    assert "operator_approval" in review_scenarios
    assert state["analytics"]["lead_count"] == 3
    assert state["analytics"]["provider_send_failures"] == 0


def test_demo_tenant_contains_no_real_customer_pii() -> None:
    state = build_demo_state()
    searchable_text = json.dumps(
        {
            "tenant": state["tenant"],
            "leads": state["leads"],
            "review_tasks": state["review_tasks"],
        }
    )

    assert not re.search(r"\b[\w.+-]+@[\w.-]+\.\w+\b", searchable_text)
    assert not re.search(r"\+?\d[\d\s().-]{7,}\d", searchable_text)
    assert "customer" not in searchable_text.lower()
    assert "phone" not in searchable_text.lower()


def test_reset_demo_tenant_restores_known_state(tmp_path: Path) -> None:
    output_path = tmp_path / "state.json"
    output_path.write_text('{"dirty": true}', encoding="utf-8")

    state = reset_demo_tenant(output_path=output_path)
    restored = json.loads(output_path.read_text(encoding="utf-8"))

    assert restored == state
    assert restored["tenant"]["tenant_id"] == "demo-garage-door"
    assert [lead["lead_id"] for lead in restored["leads"]] == [
        "demo-supported-faq",
        "demo-unsupported-handoff",
        "demo-booking-proposal",
    ]


def test_reset_demo_tenant_cli_outputs_summary(tmp_path: Path) -> None:
    output_path = tmp_path / "state.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reset_demo_tenant.py",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads(result.stdout)
    restored = json.loads(output_path.read_text(encoding="utf-8"))
    assert summary == {
        "schema_version": "demo-tenant-state-v1",
        "tenant_id": "demo-garage-door",
        "lead_count": 3,
        "review_task_count": 1,
        "reset_path": str(output_path),
    }
    assert restored["review_tasks"][0]["scenario"] == "operator_approval"
