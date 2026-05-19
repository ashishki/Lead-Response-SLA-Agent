from __future__ import annotations

from pathlib import Path

import pytest

from lead_sla_agent.retrieval.eval import compute_seed_metrics


def test_retrieval_eval_metadata_initialized() -> None:
    content = Path("docs/retrieval_eval.md").read_text(encoding="utf-8")

    assert "Embedding model | `local-hash-embedding-v1`" in content
    assert "Index schema version | `rag-index-v1`" in content
    assert "Chunking strategy | markdown-heading-v1" in content
    assert "Seed dataset path: `tests/eval/fixtures/retrieval_seed.json`" in content
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
