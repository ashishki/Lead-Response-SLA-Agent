from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_paused_reference_routes_only_reproducible_defects() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "reproducible-bug.yml").read_text(
        encoding="utf-8"
    )
    config = (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    readme_normalized = " ".join(readme.split())
    security_normalized = " ".join(security.split())

    assert "template=reproducible-bug.yml" in readme
    assert "not a feature roadmap" in readme_normalized
    assert "name: Reproducible reference defect" in form
    for field_id in (
        "revision",
        "surface",
        "environment",
        "reproduction",
        "observed",
        "expected",
        "evidence_boundary",
        "confirmations",
    ):
        assert f"id: {field_id}" in form
    assert "no real lead/contact data" in form
    assert "does not accept generic feature" in form
    assert "blank_issues_enabled: false" in config
    assert "security/policy" in config
    assert "security/advisories/new" not in config
    assert "GitHub private vulnerability reporting is not assumed" in security
    assert "cannot promise a response or remediation deadline" in security_normalized
