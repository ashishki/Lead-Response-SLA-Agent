from __future__ import annotations

import ast
from pathlib import Path

REPOSITORY_MODULES = [Path("src/lead_sla_agent/db/repositories.py")]


def test_repository_sql_uses_named_parameters() -> None:
    for module_path in REPOSITORY_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

        for node in ast.walk(tree):
            assert not isinstance(node, ast.JoinedStr), f"f-string found in {module_path}"
            assert not _is_percent_format(node), f"percent SQL formatting found in {module_path}"
            assert not _is_string_concat(node), f"string concatenation found in {module_path}"


def _is_percent_format(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and _contains_string(node.left)
    )


def _is_string_concat(node: ast.AST) -> bool:
    return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and _contains_string(node)


def _contains_string(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Constant) and isinstance(child.value, str) for child in ast.walk(node)
    )
