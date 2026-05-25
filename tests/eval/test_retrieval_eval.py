from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lead_sla_agent.retrieval.eval import compute_seed_metrics

PILOT_FIXTURE = Path("tests/eval/fixtures/retrieval_pilot_seed.json")
REQUIRED_PILOT_SLICES = {
    "pricing",
    "service_area",
    "cancellation",
    "booking",
    "exact_terms",
    "unsupported",
    "stale",
    "tenant_isolation",
}


def test_retrieval_eval_metadata_initialized() -> None:
    content = Path("docs/retrieval_eval.md").read_text(encoding="utf-8")

    assert "Deterministic embedding model | `local-hash-embedding-v1`" in content
    assert "Production embedding model | `text-embedding-3-small`" in content
    assert "Production embedding dimensions | `1536`" in content
    assert "Index schema version | `rag-index-v1`" in content
    assert "Chunking strategy | markdown-heading-v1" in content
    assert "Seed dataset path: `tests/eval/fixtures/retrieval_seed.json`" in content
    assert (
        "Operator feedback candidate path: `tests/eval/fixtures/operator_feedback_candidates.json`"
        in content
    )
    assert (
        "Vertical garage door pack eval path: "
        "`seed/verticals/garage_door_repair/retrieval_eval.json`" in content
    )
    assert (
        "Vertical public corpus seed path: "
        "`seed/verticals/garage_door_repair/public_corpus.json`" in content
    )
    assert "Baseline status | T10 seed retrieval baseline established" in content


@pytest.mark.asyncio
async def test_retrieval_eval_computes_seed_metrics() -> None:
    metrics = await compute_seed_metrics(Path("tests/eval/fixtures/retrieval_seed.json"))
    content = Path("docs/retrieval_eval.md").read_text(encoding="utf-8")

    assert metrics["hit@3"] == 1
    assert metrics["hit@5"] == 1
    assert metrics["MRR"] == 1
    assert metrics["citation_precision"] == 1
    assert metrics["no_answer_accuracy"] == 1
    assert metrics["retrieval_p95_latency_ms"] >= 0
    assert "hit@3=1.00; hit@5=1.00; MRR=1.00" in content
    assert "citation_precision=1.00; no-answer accuracy=1.00" in content
    assert "T28" in content
    assert (
        "production embedding baseline: model=`text-embedding-3-small`, dimensions=1536" in content
    )
    assert "T29" in content
    assert "admin upload/list/disable/reindex pass=100%" in content


def test_pilot_retrieval_fixture_has_required_question_slices() -> None:
    dataset = json.loads(PILOT_FIXTURE.read_text(encoding="utf-8"))
    queries = dataset["queries"]
    slices = {query["slice"] for query in queries}

    assert len(queries) >= 50
    assert slices >= REQUIRED_PILOT_SLICES
    for query in queries:
        assert query["tenant_id"]
        assert query["query"]
        assert query["expected_status"] in {"evidence", "insufficient_evidence"}
        assert isinstance(query["expected_source_document_ids"], list)


def test_pilot_retrieval_fixture_contains_no_raw_customer_pii() -> None:
    dataset = json.loads(PILOT_FIXTURE.read_text(encoding="utf-8"))
    content = json.dumps(
        {
            "documents": [
                {"source_title": document["source_title"], "text": document["text"]}
                for document in dataset["documents"]
            ],
            "queries": [query["query"] for query in dataset["queries"]],
        }
    )

    assert not re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", content)
    assert not re.search(r"\+?\d[\d\s().-]{7,}\d", content)
    for forbidden in ("Customer:", "Agent:", "private appointment details"):
        assert forbidden not in content


def test_retrieval_eval_records_valid_t30_history_row() -> None:
    content = Path("docs/retrieval_eval.md").read_text(encoding="utf-8")

    assert "T30" in content
    assert "tests/eval/fixtures/retrieval_pilot_seed.json" in content
    assert "pilot dataset validation pass=100%" in content
    assert "Root cause" in content
    assert "T33" in content
    assert "accepted operator feedback retrieval candidates=1" in content
    assert "T35" in content
    assert "vertical corpus documents=5" in content
    assert "T71" in content
    assert "public source records=35" in content
    assert "private-source and ROI/autonomous-send claim gate pass=100%" in content
    assert "T73" in content
    assert "vertical corpus documents=12" in content
    assert "public eval queries=10" in content
    assert "unsupported public queries=3" in content
