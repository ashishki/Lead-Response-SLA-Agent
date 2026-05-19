from __future__ import annotations

from pathlib import Path

import pytest

from lead_sla_agent.retrieval.eval import assert_no_answer_baseline


def test_active_eval_artifacts_have_baseline_rows() -> None:
    retrieval = Path("docs/retrieval_eval.md").read_text(encoding="utf-8")
    tool = Path("docs/tool_eval.md").read_text(encoding="utf-8")
    agent = Path("docs/agent_eval.md").read_text(encoding="utf-8")

    assert "2026-05-19 | T10" in retrieval
    assert "Eval Source" in retrieval
    assert "`rag-index-v1`" in retrieval
    assert "tests/eval/fixtures/retrieval_seed.json" in retrieval
    assert "code-change-induced" in retrieval
    assert "Any false answer for unsupported query is P1" in retrieval

    assert "2026-05-19 | T12" in tool
    assert "`tool-schema-v1`" in tool
    assert "call success rate=100%" in tool
    assert "Any missing-key write execution is P1" in tool

    assert "2026-05-19 | T13" in agent
    assert "`agent-loop-v1`" in agent
    assert "allowed-action accuracy=100%" in agent
    assert "Any action outside allowed set is P1" in agent


def test_retrieval_no_answer_regression_fails_eval() -> None:
    with pytest.raises(AssertionError, match="no-answer accuracy regression"):
        assert_no_answer_baseline({"no_answer_accuracy": 0.5})
