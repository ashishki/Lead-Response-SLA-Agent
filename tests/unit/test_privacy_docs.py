from __future__ import annotations

from pathlib import Path


def test_privacy_doc_explains_collection_retention_export_delete_and_subprocessors() -> None:
    content = Path("docs/legal/privacy.md").read_text(encoding="utf-8")

    for section in (
        "Data We Collect",
        "Retention",
        "Export",
        "Delete And Anonymize",
        "Subprocessors And Infrastructure",
    ):
        assert f"## {section}" in content
    for data_category in (
        "Lead contact data",
        "Conversation data",
        "Review data",
        "Provider metadata",
        "Operational audit data",
        "Usage data",
    ):
        assert data_category in content
    assert "Default pilot retention is 90 days" in content
    assert "Tenant export schema version: `tenant-export-v1`" in content
    assert "`tenant_data_anonymized`" in content
    for subprocessor in (
        "VPS host",
        "PostgreSQL",
        "Redis",
        "Grafana Cloud",
        "Twilio WhatsApp",
        "Telegram Bot API",
        "OpenAI embedding API",
    ):
        assert subprocessor in content


def test_dpa_notes_define_supported_and_unsupported_commitments() -> None:
    content = Path("docs/legal/dpa_notes.md").read_text(encoding="utf-8")

    for section in (
        "Roles",
        "Supported Commitments",
        "Unsupported Or Not Yet Promised",
        "Required Order Form Inputs",
        "Subprocessor Change Procedure",
    ):
        assert f"## {section}" in content
    assert "Use v1 anonymization" in content
    assert "default pilot retention is 90 days" in content
    for unsupported in (
        "hard deletion of all database rows",
        "zero-retention operation",
        "autonomous outbound sends without human approval",
        "broad paid production readiness",
    ):
        assert unsupported in content


def test_runbook_documents_retention_enforcement_drill() -> None:
    content = Path("docs/runbook.md").read_text(encoding="utf-8")

    assert "Retention enforcement procedure" in content
    assert "tenant_retention_applied" in content
    assert "tests/integration/test_data_retention.py" in content
    assert "export artifacts" in content
