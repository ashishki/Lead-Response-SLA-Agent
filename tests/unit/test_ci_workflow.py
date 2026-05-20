from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW_PATH = Path(".github/workflows/ci.yml")
DEPLOY_WORKFLOW_PATH = Path(".github/workflows/deploy.yml")


def load_workflow() -> dict:
    with WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        return yaml.safe_load(workflow_file)


def test_ci_workflow_has_required_steps() -> None:
    workflow = load_workflow()
    jobs = workflow["jobs"]

    assert {"lint_format", "unit", "integration", "eval", "deployment_checks"} <= set(jobs)
    assert {step.get("name") for step in jobs["lint_format"]["steps"]} >= {
        "Lint",
        "Format check",
    }
    assert {step.get("name") for step in jobs["unit"]["steps"]} >= {"Run unit tests"}
    assert {step.get("name") for step in jobs["integration"]["steps"]} >= {"Run integration tests"}
    assert {step.get("name") for step in jobs["eval"]["steps"]} >= {
        "Retrieval eval",
        "Tool-use eval",
        "Agent eval",
        "Operator feedback eval",
    }
    assert {step.get("name") for step in jobs["deployment_checks"]["steps"]} >= {
        "Deployment docs and secret policy"
    }


def test_ci_workflow_declares_required_services() -> None:
    workflow = load_workflow()
    services = workflow["jobs"]["integration"]["services"]

    assert "postgres" in services
    assert "redis" in services

    for service_name in ("postgres", "redis"):
        service = services[service_name]
        assert "image" in service
        assert "--health-cmd" in service["options"]
        assert "--health-interval" in service["options"]
        assert "--health-timeout" in service["options"]
        assert "--health-retries" in service["options"]


def test_ci_workflow_sets_required_integration_env() -> None:
    workflow = load_workflow()
    run_tests_step = next(
        step
        for step in workflow["jobs"]["integration"]["steps"]
        if step.get("name") == "Run integration tests"
    )

    assert run_tests_step["env"]["APP_ENV"] == "test"
    assert run_tests_step["env"]["DATABASE_URL"].startswith("postgresql+asyncpg://")
    assert run_tests_step["env"]["REDIS_URL"] == "redis://localhost:6379/0"
    assert "OPERATOR_AUTH_SECRET" in run_tests_step["env"]


def test_deploy_workflow_requires_staging_before_production() -> None:
    with DEPLOY_WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        workflow = yaml.safe_load(workflow_file)
    jobs = workflow["jobs"]

    assert {"staging_deploy", "production_deploy"} <= set(jobs)
    assert jobs["staging_deploy"]["environment"] == "staging"
    assert jobs["production_deploy"]["environment"] == "production"
    assert jobs["production_deploy"]["needs"] == "staging_deploy"
    staging_steps = {step.get("name") for step in jobs["staging_deploy"]["steps"]}
    production_steps = {step.get("name") for step in jobs["production_deploy"]["steps"]}
    assert {"Run staging migrations", "Run staging smoke tests", "Validate rollback command"} <= (
        staging_steps
    )
    assert {
        "Run production migrations",
        "Run production smoke tests",
        "Validate rollback assets",
    } <= (production_steps)


def test_release_template_tracks_model_eval_and_rollback_changes() -> None:
    content = Path("docs/release_template.md").read_text(encoding="utf-8")

    for required in (
        "Model, Prompt, Schema, And Eval Changes",
        "Prompt version",
        "Model output schema",
        "Retrieval index schema",
        "Tool schema",
        "Eval fixtures or metrics",
        "Rollback Plan",
        "Database backup path",
    ):
        assert required in content
