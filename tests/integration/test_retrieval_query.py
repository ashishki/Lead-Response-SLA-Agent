from __future__ import annotations

import uuid
from datetime import date

import pytest

from lead_sla_agent.retrieval.documents import FetchedKnowledgeDocument, SourceDocumentRef
from lead_sla_agent.retrieval.embeddings import DeterministicHashEmbeddingClient
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex, KnowledgeIngestionPipeline
from lead_sla_agent.retrieval.query import InMemoryHumanReviewSink, RetrievalQueryService

TENANT_A = uuid.UUID("00000000-0000-4000-8000-0000000000a1")
TENANT_B = uuid.UUID("00000000-0000-4000-8000-0000000000b1")


async def build_index() -> InMemoryKnowledgeIndex:
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)
    await pipeline.ingest_markdown_document(
        FetchedKnowledgeDocument(
            ref=SourceDocumentRef(TENANT_A, "tenant-a-faq", "Tenant A FAQ", date(2026, 5, 19)),
            text="# Service Area\nTenant A serves downtown and northside neighborhoods.",
        )
    )
    await pipeline.ingest_markdown_document(
        FetchedKnowledgeDocument(
            ref=SourceDocumentRef(TENANT_B, "tenant-b-faq", "Tenant B FAQ", date(2026, 5, 19)),
            text="# Service Area\nTenant B serves lakeside and airport neighborhoods.",
        )
    )
    return index


@pytest.mark.asyncio
async def test_retrieval_is_tenant_scoped() -> None:
    review_sink = InMemoryHumanReviewSink()
    service = RetrievalQueryService(await build_index(), review_sink)

    result = await service.retrieve(TENANT_A, "Do you serve lakeside or downtown?", limit=5)

    assert result.status == "evidence"
    assert {evidence.tenant_id for evidence in result.evidence} == {TENANT_A}
    assert {evidence.source_document_id for evidence in result.evidence} == {"tenant-a-faq"}


@pytest.mark.asyncio
async def test_unsupported_query_creates_insufficient_evidence_handoff() -> None:
    review_sink = InMemoryHumanReviewSink()
    service = RetrievalQueryService(await build_index(), review_sink)

    result = await service.retrieve(TENANT_A, "Can you write a legal contract for me?")

    assert result.status == "insufficient_evidence"
    assert result.answer_text is None
    assert result.evidence == []
    assert result.human_review_task is not None
    assert result.human_review_task.reason == "insufficient_evidence"
    assert review_sink.tasks == [result.human_review_task]
