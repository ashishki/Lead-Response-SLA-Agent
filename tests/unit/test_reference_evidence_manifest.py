from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs/evidence/reference_evidence_manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_reference_evidence_manifest_seals_existing_artifacts() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "lead-sla-reference-evidence-v1"
    assert manifest["data_classification"] == "synthetic_fixture_only"
    assert manifest["source_revision"] == "7fa6ad2d2ec188c83b1e696f6ea232562811eac1"
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file()
        assert _sha256(path) == artifact["sha256"]


def test_reference_evidence_keeps_product_claims_closed() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    summary = manifest["observed_fixture_summary"]

    assert summary == {
        "failure_case_count": 7,
        "human_approval_required_count": 50,
        "scenario_count": 50,
        "unsafe_autonomous_send_count": 0,
    }
    assert set(manifest["claim_boundary"].values()) == {False}

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ledger = (ROOT / "docs/REFERENCE_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
    assert "paused reference implementation" in readme
    assert "Реального pilot tenant" in readme
    assert "fixture-level reference evidence" in ledger
    assert "does not establish" in ledger
