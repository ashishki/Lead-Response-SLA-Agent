from __future__ import annotations

import tomllib
from pathlib import Path


def test_unit_and_integration_tests_exist() -> None:
    unit_tests = list(Path("tests/unit").glob("test_*.py"))
    integration_tests = list(Path("tests/integration").glob("test_*.py"))

    assert unit_tests
    assert integration_tests


def test_ruff_commands_declared_in_pyproject() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["tool"]["ruff"]["target-version"] == "py312"
    assert pyproject["tool"]["ruff"]["line-length"] == 100
    assert pyproject["tool"]["ruff"]["lint"]["select"]
    assert pyproject["tool"]["ruff"]["format"]["quote-style"] == "double"
