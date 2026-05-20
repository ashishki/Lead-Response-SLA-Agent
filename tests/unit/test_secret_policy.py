from __future__ import annotations

import re
from pathlib import Path

import yaml

API_ENV = {
    "APP_ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "OPERATOR_AUTH_SECRET",
    "WEBHOOK_SHARED_SECRET",
}
WORKER_ENV = {
    "APP_ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "EMAIL_API_KEY",
    "EMAIL_SENDER",
    "EMAIL_API_URL",
    "CALENDAR_API_TOKEN",
    "CALENDAR_API_URL",
    "CRM_API_TOKEN",
    "CRM_API_URL",
    "EMBEDDING_API_KEY",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSIONS",
    "EMBEDDING_API_URL",
    "MAX_AUTONOMOUS_TURNS",
    "MAX_TOOL_CALLS_PER_TURN",
    "MAX_INDEX_AGE_HOURS",
}
REAL_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def test_compose_scopes_api_and_worker_environment_variables() -> None:
    compose = yaml.safe_load(Path("compose.yml").read_text(encoding="utf-8"))

    assert set(compose["services"]["api"]["environment"]) == API_ENV
    assert set(compose["services"]["worker"]["environment"]) == WORKER_ENV
    assert "WEBHOOK_SHARED_SECRET" not in compose["services"]["worker"]["environment"]
    assert "OPERATOR_AUTH_SECRET" not in compose["services"]["worker"]["environment"]
    assert "EMAIL_API_KEY" not in compose["services"]["api"]["environment"]
    assert "CRM_API_TOKEN" not in compose["services"]["api"]["environment"]


def test_runbook_documents_secret_sources_and_rotation() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    for secret_name in (
        "DATABASE_URL",
        "REDIS_URL",
        "OPERATOR_AUTH_SECRET",
        "WEBHOOK_SHARED_SECRET",
        "EMAIL_API_KEY",
        "CALENDAR_API_TOKEN",
        "CRM_API_TOKEN",
        "EMBEDDING_API_KEY",
        "POSTGRES_PASSWORD",
    ):
        assert secret_name in content
    assert "Environment Partitions" in content
    assert "Rotation Procedure" in content
    assert "The API container receives only" in content
    assert "The worker container receives only" in content


def test_docs_and_fixtures_do_not_contain_real_looking_credentials() -> None:
    scanned_paths = [
        path
        for root in (Path("docs"), Path("seed"), Path("tests/eval/fixtures"))
        for path in root.rglob("*")
        if path.is_file()
    ]
    scanned_paths.append(Path("compose.yml"))

    findings: list[str] = []
    for path in scanned_paths:
        content = path.read_text(encoding="utf-8")
        for pattern in REAL_SECRET_PATTERNS:
            if pattern.search(content):
                findings.append(str(path))

    assert findings == []


def test_no_dotenv_files_are_committed() -> None:
    dotenv_files = [
        path for path in Path(".").rglob(".env*") if ".git" not in path.parts and path.is_file()
    ]

    assert dotenv_files == []
