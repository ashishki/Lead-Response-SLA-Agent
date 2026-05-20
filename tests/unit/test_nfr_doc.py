from __future__ import annotations

from pathlib import Path


def test_nfr_doc_contains_required_targets() -> None:
    content = Path("docs/nfr.md").read_text(encoding="utf-8")

    assert "AI-assisted first-response p95 | below 30 seconds" in content
    assert "deterministic acknowledgement p95 | below 2 seconds" in content
    assert "query-time retrieval p95 | below 2 seconds" in content
    assert "provider send failure rate | below 2 percent in pilot fake-provider path" in content
    assert "T17" in content
    assert "T36" in content
    assert "GET /operator/analytics/weekly" in content
    assert "first_response_latency_p50_ms" in content
    assert "weekly_report" in content
