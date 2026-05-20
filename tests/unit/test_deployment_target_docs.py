from __future__ import annotations

from pathlib import Path

import yaml

ADR_PATH = Path("docs/adr/ADR-004-deployment-target.md")
RUNBOOK_PATH = Path("docs/runbook.md")
DEPLOY_WORKFLOW_PATH = Path(".github/workflows/deploy.yml")
CI_WORKFLOW_PATH = Path(".github/workflows/ci.yml")
ALEMBIC_INI_PATH = Path("alembic.ini")
ALEMBIC_ENV_PATH = Path("alembic/env.py")


def test_deployment_target_adr_names_vps_and_rejected_alternatives() -> None:
    content = ADR_PATH.read_text(encoding="utf-8")

    assert "Use a VPS with Docker Compose" in content
    assert "Runtime tier remains T1" in content
    assert "Render" in content
    assert "Railway" in content
    assert "AWS ECS" in content
    assert "T2/T3" in content


def test_deployment_target_adr_lists_required_staging_and_production_resources() -> None:
    content = ADR_PATH.read_text(encoding="utf-8")

    for required in (
        "| staging | 1 VPS running Docker Compose API, worker, PostgreSQL, Redis |",
        "| production | 1 VPS running Docker Compose API, worker, PostgreSQL, Redis |",
        "founder/operator",
        "daily PostgreSQL custom-format dump and pre-migration dump",
        "30 days minimum during pilot",
        "low fixed monthly VPS cost",
    ):
        assert required in content


def test_runbook_documents_vps_resource_contract_and_commands() -> None:
    content = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "## Deployment Target" in content
    assert "VPS with Docker Compose" in content
    assert "founder/operator" in content
    assert "Concrete staging deploy command" in content
    assert "Concrete production deploy command" in content
    assert "Concrete app rollback command" in content
    assert "docker compose run --rm api alembic upgrade head" in content
    assert "scripts/backup_postgres.sh" in content
    assert "git checkout $ROLLBACK_GIT_SHA" in content


def test_deploy_workflow_uses_vps_ssh_deploy_migration_smoke_and_rollback_validation() -> None:
    workflow = yaml.safe_load(DEPLOY_WORKFLOW_PATH.read_text(encoding="utf-8"))
    jobs = workflow["jobs"]

    assert jobs["staging_deploy"]["environment"] == "staging"
    assert jobs["production_deploy"]["environment"] == "production"
    assert jobs["production_deploy"]["needs"] == "staging_deploy"
    assert "STAGING_VPS_HOST" in str(jobs["staging_deploy"])
    assert "PRODUCTION_VPS_HOST" in str(jobs["production_deploy"])
    workflow_text = DEPLOY_WORKFLOW_PATH.read_text(encoding="utf-8")
    for required in (
        'ssh "$STAGING_SSH_TARGET"',
        'ssh "$PRODUCTION_SSH_TARGET"',
        "docker compose config",
        "docker compose run --rm api alembic upgrade head",
        "docker compose exec -T api python scripts/smoke_test.py --environment staging",
        "docker compose exec -T api python scripts/smoke_test.py --environment production",
        "BACKUP_PATH=backups/pre-migration-$GITHUB_SHA.dump ./scripts/backup_postgres.sh",
        "git rev-parse --verify '${{ github.event.inputs.rollback_git_sha }}'",
    ):
        assert required in workflow_text


def test_deployment_target_checks_are_part_of_ci_deployment_gate() -> None:
    workflow_text = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "tests/unit/test_deployment_target_docs.py" in workflow_text


def test_alembic_config_supports_deployment_migration_command() -> None:
    ini_content = ALEMBIC_INI_PATH.read_text(encoding="utf-8")
    env_content = ALEMBIC_ENV_PATH.read_text(encoding="utf-8")

    assert "script_location = alembic" in ini_content
    assert "sqlalchemy.url = postgresql+asyncpg://" in ini_content
    assert 'os.environ.get("DATABASE_URL")' in env_content
    assert "async_engine_from_config" in env_content
