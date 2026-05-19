from __future__ import annotations

import ast
from pathlib import Path

from lead_sla_agent.observability.tracing import get_tracer


def test_shared_tracing_import_contract() -> None:
    tracer = get_tracer("lead_sla_agent.tests")
    assert tracer is not None

    tracing_module = Path("src/lead_sla_agent/observability/tracing.py")
    for path in Path("src/lead_sla_agent").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "opentelemetry":
                assert path == tracing_module
            if isinstance(node, ast.ImportFrom) and node.module == "opentelemetry.trace":
                assert path == tracing_module
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "get_tracer" for alias in node.names
            ):
                assert node.module == "lead_sla_agent.observability.tracing"
