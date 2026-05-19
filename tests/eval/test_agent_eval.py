from __future__ import annotations

from pathlib import Path


def test_agent_eval_metadata_initialized() -> None:
    content = Path("docs/agent_eval.md").read_text(encoding="utf-8")

    assert "Loop contract version | `agent-loop-v1`" in content
    assert "allowed-action accuracy=100%" in content
    assert "termination reason accuracy=100%" in content
    assert "handoff integrity=100%" in content
    assert "tool-call budget enforcement=100%" in content
    assert "T13" in content
