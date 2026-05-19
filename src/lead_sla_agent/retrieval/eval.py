"""Retrieval seed evaluation helpers."""

from __future__ import annotations

import json
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from lead_sla_agent.retrieval.documents import FetchedKnowledgeDocument, SourceDocumentRef
from lead_sla_agent.retrieval.embeddings import DeterministicHashEmbeddingClient
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex, KnowledgeIngestionPipeline
from lead_sla_agent.retrieval.query import InMemoryHumanReviewSink, RetrievalQueryService


def assert_no_answer_baseline(metrics: dict[str, float]) -> None:
    """Fail the retrieval gate on any no-answer accuracy regression."""
    if metrics["no_answer_accuracy"] < 1:
        raise AssertionError("no-answer accuracy regression")


async def compute_seed_metrics(dataset_path: Path) -> dict[str, float]:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)
    for document in dataset["documents"]:
        await pipeline.ingest_markdown_document(_document_from_json(document))

    review_sink = InMemoryHumanReviewSink()
    service = RetrievalQueryService(index, review_sink)
    query_count = len(dataset["queries"])
    hit_at_3 = 0
    hit_at_5 = 0
    reciprocal_rank = 0.0
    citation_precision = 0.0
    no_answer_correct = 0
    no_answer_total = 0
    latencies: list[float] = []

    for query in dataset["queries"]:
        start = time.perf_counter()
        result = await service.retrieve(uuid.UUID(query["tenant_id"]), query["query"], limit=5)
        latencies.append((time.perf_counter() - start) * 1000)
        expected_ids = set(query["expected_source_document_ids"])
        returned_ids = [evidence.source_document_id for evidence in result.evidence]

        if query["expected_status"] == "insufficient_evidence":
            no_answer_total += 1
            if result.status == "insufficient_evidence" and result.answer_text is None:
                no_answer_correct += 1
            continue

        if expected_ids & set(returned_ids[:3]):
            hit_at_3 += 1
        if expected_ids & set(returned_ids[:5]):
            hit_at_5 += 1
        for index_position, source_document_id in enumerate(returned_ids, start=1):
            if source_document_id in expected_ids:
                reciprocal_rank += 1 / index_position
                break
        returned_id_set = set(returned_ids)
        if returned_id_set:
            citation_precision += len(expected_ids & returned_id_set) / len(returned_id_set)

    supported_count = query_count - no_answer_total
    return {
        "hit@3": hit_at_3 / supported_count,
        "hit@5": hit_at_5 / supported_count,
        "MRR": reciprocal_rank / supported_count,
        "citation_precision": citation_precision / supported_count,
        "no_answer_accuracy": no_answer_correct / no_answer_total,
        "retrieval_p95_latency_ms": max(latencies),
    }


def _document_from_json(raw_document: dict[str, Any]) -> FetchedKnowledgeDocument:
    return FetchedKnowledgeDocument(
        ref=SourceDocumentRef(
            tenant_id=uuid.UUID(raw_document["tenant_id"]),
            source_document_id=raw_document["source_document_id"],
            source_title=raw_document["source_title"],
            effective_date=date.fromisoformat(raw_document["effective_date"]),
        ),
        text=raw_document["text"],
    )
