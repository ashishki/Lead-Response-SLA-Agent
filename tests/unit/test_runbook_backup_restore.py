from __future__ import annotations

from pathlib import Path


def test_runbook_documents_backup_restore_drill() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    for phrase in (
        "Backup schedule",
        "Backup command",
        "Restore command",
        "Restore verification checklist",
        "Local restore drill",
        "VERIFY_COMMAND",
        "tenant-scoped repository tests",
    ):
        assert phrase in content


def test_backup_restore_scripts_use_database_url_and_verification_command() -> None:
    backup_script = Path("scripts/backup_postgres.sh")
    restore_script = Path("scripts/restore_postgres.sh")

    assert backup_script.exists()
    assert restore_script.exists()
    assert "pg_dump" in backup_script.read_text(encoding="utf-8")
    assert "DATABASE_URL is required" in backup_script.read_text(encoding="utf-8")
    assert "pg_restore" in restore_script.read_text(encoding="utf-8")
    assert "VERIFY_COMMAND" in restore_script.read_text(encoding="utf-8")


def test_migrations_have_downgrade_paths_or_rationale() -> None:
    migration_paths = sorted(Path("alembic/versions").glob("*.py"))

    assert migration_paths
    for path in migration_paths:
        content = path.read_text(encoding="utf-8")
        assert "def downgrade() -> None:" in content
        assert "pass" not in content
