"""Text-only knowledge ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from lead_sla_agent.retrieval.chunking import (
    CHUNKING_STRATEGY,
    INDEX_SCHEMA_VERSION,
    KnowledgeChunkDraft,
    chunk_markdown_document,
)
from lead_sla_agent.retrieval.documents import (
    FetchedKnowledgeDocument,
    normalize_text_document,
)
from lead_sla_agent.retrieval.embeddings import EmbeddingClient


@dataclass(frozen=True)
class IndexedKnowledgeChunk:
    chunk: KnowledgeChunkDraft
    embedding: list[float]
    embedding_model: str


class InMemoryKnowledgeIndex:
    """Tenant-scoped in-memory index used by local ingestion tests."""

    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, int, str], IndexedKnowledgeChunk] = {}

    def upsert_chunks(self, chunks: list[IndexedKnowledgeChunk]) -> list[IndexedKnowledgeChunk]:
        indexed: list[IndexedKnowledgeChunk] = []
        for chunk in chunks:
            key = (
                str(chunk.chunk.tenant_id),
                chunk.chunk.source_document_id,
                chunk.chunk.chunk_ordinal,
                chunk.chunk.index_schema_version,
            )
            existing = self.rows.get(key)
            if existing is not None and existing.chunk.content_hash == chunk.chunk.content_hash:
                indexed.append(existing)
                continue

            self.rows[key] = chunk
            indexed.append(chunk)
        return indexed

    def list_chunks(self) -> list[IndexedKnowledgeChunk]:
        return list(self.rows.values())


class KnowledgeIngestionPipeline:
    """Normalize, chunk, embed, and index approved text knowledge documents."""

    def __init__(self, embedding_client: EmbeddingClient, index: InMemoryKnowledgeIndex) -> None:
        self.embedding_client = embedding_client
        self.index = index

    async def ingest_markdown_document(
        self,
        document: FetchedKnowledgeDocument,
    ) -> list[IndexedKnowledgeChunk]:
        normalized = normalize_text_document(document)
        chunk_drafts = chunk_markdown_document(normalized)
        embeddings = await self.embedding_client.embed_texts(
            [chunk.content for chunk in chunk_drafts]
        )
        chunks = [
            IndexedKnowledgeChunk(
                chunk=chunk,
                embedding=embedding,
                embedding_model=self.embedding_client.model_name,
            )
            for chunk, embedding in zip(chunk_drafts, embeddings, strict=True)
        ]
        return self.index.upsert_chunks(chunks)


__all__ = [
    "CHUNKING_STRATEGY",
    "INDEX_SCHEMA_VERSION",
    "IndexedKnowledgeChunk",
    "InMemoryKnowledgeIndex",
    "KnowledgeIngestionPipeline",
]
