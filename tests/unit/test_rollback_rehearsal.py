from __future__ import annotations

from pathlib import Path

import yaml

from scripts import rollback_check


def test_all_alembic_migrations_have_downgrade_coverage_or_rationale() -> None:
    checks = rollback_check.check_migration_files(Path("alembic/versions"))

    assert checks
    assert all(check.status == "ok" for check in checks)
    assert all(check.has_downgrade_coverage or check.has_irreversible_rationale for check in checks)


def test_migration_check_rejects_empty_downgrade_without_rationale(tmp_path: Path) -> None:
    migration = tmp_path / "0008_bad.py"
    migration.write_text(
        'revision = "0008_bad"\n'
        'down_revision = "0007_audit_events"\n\n'
        "def upgrade() -> None:\n"
        "    print('upgrade')\n\n"
        "def downgrade() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )

    check = rollback_check.check_migration_file(migration)

    assert check.status == "missing"
    assert not check.has_downgrade_coverage


def test_migration_check_accepts_explicit_irreversible_rationale(tmp_path: Path) -> None:
    migration = tmp_path / "0008_irreversible.py"
    migration.write_text(
        '"""Irreversible rationale: drops derived cache data that can be rebuilt."""\n\n'
        'revision = "0008_irreversible"\n'
        'down_revision = "0007_audit_events"\n\n'
        "def upgrade() -> None:\n"
        "    print('upgrade')\n",
        encoding="utf-8",
    )

    check = rollback_check.check_migration_file(migration)

    assert check.status == "ok"
    assert check.has_irreversible_rationale


def test_rollback_rehearsal_artifact_records_before_and_after_versions() -> None:
    missing = rollback_check.check_rehearsal_artifact(Path("docs/rollback_rehearsal.md"))

    assert missing == []
    content = Path("docs/rollback_rehearsal.md").read_text(encoding="utf-8")
    assert "migration_version_before:" in content
    assert "migration_version_after:" in content
    assert "alembic downgrade -1" in content
    assert "alembic upgrade head" in content


def test_rollback_check_report_fails_when_rehearsal_artifact_is_incomplete(tmp_path: Path) -> None:
    artifact = tmp_path / "rollback_rehearsal.md"
    artifact.write_text("environment: staging\n", encoding="utf-8")

    report = rollback_check.build_report(
        versions_dir=Path("alembic/versions"),
        rehearsal_artifact=artifact,
    )

    assert not report.ok
    assert "migration_version_before:" in report.missing_rehearsal_fields


def test_runbook_defines_app_migration_and_backup_rollback_decisions() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "App-only rollback" in content
    assert "Migration rollback" in content
    assert "Restore from backup" in content
    assert "migration version before rollback" in content
    assert "migration version after rollback" in content


def test_deploy_workflow_validates_rollback_rehearsal_before_production_deploy() -> None:
    workflow_text = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    production_steps = [
        step["name"] for step in workflow["jobs"]["production_deploy"]["steps"] if "name" in step
    ]

    assert "Validate rollback rehearsal artifacts" in production_steps
    assert production_steps.index("Validate rollback rehearsal artifacts") < production_steps.index(
        "Deploy production containers"
    )
    assert "python scripts/rollback_check.py" in workflow_text
    assert "docs/rollback_rehearsal.md" in workflow_text
