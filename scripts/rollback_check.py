"""Validate rollback rehearsal artifacts and migration downgrade coverage."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REQUIRED_REHEARSAL_FIELDS = (
    "environment:",
    "release_candidate_sha:",
    "rollback_git_sha:",
    "migration_version_before:",
    "migration_version_after:",
    "rollback_decision:",
    "backup_path:",
    "smoke_result:",
)


@dataclass(frozen=True)
class MigrationRollbackCheck:
    path: str
    revision: str
    has_downgrade_coverage: bool
    has_irreversible_rationale: bool
    status: str


@dataclass(frozen=True)
class RollbackCheckReport:
    migrations: list[MigrationRollbackCheck]
    rehearsal_artifact: str
    missing_rehearsal_fields: list[str]

    @property
    def ok(self) -> bool:
        return not self.failed_migrations and not self.missing_rehearsal_fields

    @property
    def failed_migrations(self) -> list[MigrationRollbackCheck]:
        return [migration for migration in self.migrations if migration.status != "ok"]


def build_report(
    *,
    versions_dir: Path,
    rehearsal_artifact: Path,
) -> RollbackCheckReport:
    migrations = check_migration_files(versions_dir)
    missing_fields = check_rehearsal_artifact(rehearsal_artifact)
    return RollbackCheckReport(
        migrations=migrations,
        rehearsal_artifact=str(rehearsal_artifact),
        missing_rehearsal_fields=missing_fields,
    )


def check_migration_files(versions_dir: Path) -> list[MigrationRollbackCheck]:
    migration_paths = sorted(versions_dir.glob("*.py"))
    if not migration_paths:
        raise RuntimeError(f"no migration files found in {versions_dir}")
    return [check_migration_file(path) for path in migration_paths]


def check_migration_file(path: Path) -> MigrationRollbackCheck:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    revision = _revision_from_ast(tree) or path.stem
    has_downgrade_coverage = _has_downgrade_coverage(tree)
    has_irreversible_rationale = _has_irreversible_rationale(tree)
    status = "ok" if has_downgrade_coverage or has_irreversible_rationale else "missing"
    return MigrationRollbackCheck(
        path=str(path),
        revision=revision,
        has_downgrade_coverage=has_downgrade_coverage,
        has_irreversible_rationale=has_irreversible_rationale,
        status=status,
    )


def check_rehearsal_artifact(path: Path) -> list[str]:
    if not path.exists():
        return list(REQUIRED_REHEARSAL_FIELDS)

    content = path.read_text(encoding="utf-8")
    return [field for field in REQUIRED_REHEARSAL_FIELDS if field not in content]


def _revision_from_ast(tree: ast.Module) -> str | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "revision"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    return node.value.value
    return None


def _has_downgrade_coverage(tree: ast.Module) -> bool:
    downgrade = _find_function(tree, "downgrade")
    if downgrade is None:
        return False
    meaningful_nodes = [node for node in downgrade.body if not _is_noop_expr(node)]
    if not meaningful_nodes:
        return False
    if all(isinstance(node, ast.Pass) for node in meaningful_nodes):
        return False
    return not any(_raises_not_implemented(node) for node in meaningful_nodes)


def _is_noop_expr(node: ast.stmt) -> bool:
    if isinstance(node, ast.Pass):
        return True
    if not isinstance(node, ast.Expr):
        return False
    value = node.value
    return isinstance(value, ast.Constant) and (
        value.value is Ellipsis or isinstance(value.value, str)
    )


def _has_irreversible_rationale(tree: ast.Module) -> bool:
    module_docstring = ast.get_docstring(tree) or ""
    if "irreversible rationale:" in module_docstring.lower():
        return True

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "IRREVERSIBLE_RATIONALE":
                    return isinstance(node.value, ast.Constant) and bool(
                        str(node.value.value).strip()
                    )
    return False


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _raises_not_implemented(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Raise):
        return False
    exception = node.exc
    if isinstance(exception, ast.Call):
        exception = exception.func
    return isinstance(exception, ast.Name) and exception.id in {
        "NotImplementedError",
        "NotImplemented",
    }


def _report_to_dict(report: RollbackCheckReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["ok"] = report.ok
    payload["failed_migrations"] = [asdict(migration) for migration in report.failed_migrations]
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate rollback rehearsal readiness.")
    parser.add_argument("--versions-dir", default="alembic/versions")
    parser.add_argument("--rehearsal-artifact", default="docs/rollback_rehearsal.md")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        versions_dir=Path(args.versions_dir),
        rehearsal_artifact=Path(args.rehearsal_artifact),
    )
    payload = _report_to_dict(report)
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    elif report.ok:
        print("rollback_check=ok")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
