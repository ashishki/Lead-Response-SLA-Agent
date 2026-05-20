from __future__ import annotations

from pathlib import Path

import yaml


def test_ci_runs_active_profile_eval_steps() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))
    step_by_name = {
        step.get("name"): step for step in workflow["jobs"]["eval"]["steps"] if "name" in step
    }

    assert step_by_name["Retrieval eval"]["run"] == (
        "python -m pytest tests/eval/test_retrieval_eval.py -q --tb=short"
    )
    assert step_by_name["Tool-use eval"]["run"] == (
        "python -m pytest tests/eval/test_tool_eval.py -q --tb=short"
    )
    assert step_by_name["Agent eval"]["run"] == (
        "python -m pytest tests/eval/test_agent_eval.py -q --tb=short"
    )
    assert step_by_name["Operator feedback eval"]["run"] == (
        "python -m pytest tests/eval/test_operator_feedback.py -q --tb=short"
    )
