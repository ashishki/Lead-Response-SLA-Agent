from __future__ import annotations

import uuid
from datetime import date

import pytest

from lead_sla_agent.retrieval.chunking import INDEX_SCHEMA_VERSION
from lead_sla_agent.retrieval.documents import FetchedKnowledgeDocument, SourceDocumentRef
from lead_sla_agent.retrieval.embeddings import DeterministicHashEmbeddingClient
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex, KnowledgeIngestionPipeline

TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000009")


def markdown_faq() -> FetchedKnowledgeDocument:
    return FetchedKnowledgeDocument(
        ref=SourceDocumentRef(
            tenant_id=TENANT_ID,
            source_document_id="faq-001",
            source_title="Pilot FAQ",
            effective_date=date(2026, 5, 19),
        ),
        text="""
# Services
We offer emergency appointments and standard consultations.

## Booking
Same-day appointments are available when the calendar has open slots.
""",
    )


@pytest.mark.asyncio
async def test_markdown_faq_ingestion_stores_versioned_chunks() -> None:
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)

    chunks = await pipeline.ingest_markdown_document(markdown_faq())

    assert len(chunks) == 2
    for ordinal, indexed_chunk in enumerate(chunks):
        chunk = indexed_chunk.chunk
        assert chunk.tenant_id == TENANT_ID
        assert chunk.source_document_id == "faq-001"
        assert chunk.source_title == "Pilot FAQ"
        assert chunk.effective_date == date(2026, 5, 19)
        assert chunk.content_hash
        assert chunk.chunk_ordinal == ordinal
        assert chunk.index_schema_version == INDEX_SCHEMA_VERSION
        assert indexed_chunk.embedding
        assert indexed_chunk.embedding_model == "local-hash-embedding-v1"


@pytest.mark.asyncio
async def test_unchanged_source_ingestion_is_idempotent() -> None:
    index = InMemoryKnowledgeIndex()
    pipeline = KnowledgeIngestionPipeline(DeterministicHashEmbeddingClient(), index)

    first_chunks = await pipeline.ingest_markdown_document(markdown_faq())
    second_chunks = await pipeline.ingest_markdown_document(markdown_faq())

    assert len(index.list_chunks()) == len(first_chunks)
    assert [chunk.chunk.content_hash for chunk in second_chunks] == [
        chunk.chunk.content_hash for chunk in first_chunks
    ]
