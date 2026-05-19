from __future__ import annotations

from pathlib import Path


def test_tool_eval_metadata_initialized() -> None:
    content = Path("docs/tool_eval.md").read_text(encoding="utf-8")

    assert "Tool schema version | `tool-schema-v1`" in content
    assert "`send_message`, `create_or_update_lead`, `lookup_available_slots`" in content
    assert "Side-effect classes | read, write, send, book" in content
    assert "T11" in content
    assert "schema validation pass rate=100%" in content
    assert "unsafe-gate pass rate=100%" in content
    assert "idempotency rejection pass rate=100%" in content


def test_tool_eval_records_runtime_scenarios() -> None:
    content = Path("docs/tool_eval.md").read_text(encoding="utf-8")

    assert "T12" in content
    assert "call success rate=100%" in content
    assert "schema validation pass rate=100%" in content
    assert "unsafe-gate pass rate=100%" in content
    assert "provider timeout fallback scenario documented" in content
