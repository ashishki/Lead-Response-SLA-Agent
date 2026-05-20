"""Text-only knowledge ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

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


@dataclass(frozen=True)
class KnowledgeDocumentRecord:
    tenant_id: str
    source_document_id: str
    source_title: str
    text: str
    effective_date: date
    approved_knowledge: bool
    disabled: bool = False


@dataclass(frozen=True)
class ReindexRecord:
    tenant_id: str
    actor_id: str
    reindexed_at: datetime
    corpus_version: str
    index_schema_version: str
    active_document_count: int


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


class InMemoryKnowledgeAdminStore:
    """Tenant-scoped source document admin store used by operator APIs."""

    def __init__(self) -> None:
        self.documents: dict[tuple[str, str], KnowledgeDocumentRecord] = {}
        self.reindex_records: list[ReindexRecord] = []

    async def upload_document(
        self,
        tenant_id: str,
        source_document_id: str,
        source_title: str,
        text: str,
        effective_date: date,
        approved_knowledge: bool,
    ) -> KnowledgeDocumentRecord:
        if not approved_knowledge and _looks_like_customer_transcript(text):
            raise ValueError("raw customer transcript data must be marked as approved knowledge")

        record = KnowledgeDocumentRecord(
            tenant_id=tenant_id,
            source_document_id=source_document_id,
            source_title=source_title,
            text=text,
            effective_date=effective_date,
            approved_knowledge=approved_knowledge,
            disabled=False,
        )
        self.documents[(tenant_id, source_document_id)] = record
        return record

    async def list_documents(self, tenant_id: str) -> list[KnowledgeDocumentRecord]:
        return [document for document in self.documents.values() if document.tenant_id == tenant_id]

    async def disable_document(
        self,
        tenant_id: str,
        source_document_id: str,
    ) -> KnowledgeDocumentRecord | None:
        existing = self.documents.get((tenant_id, source_document_id))
        if existing is None:
            return None
        disabled = KnowledgeDocumentRecord(
            tenant_id=existing.tenant_id,
            source_document_id=existing.source_document_id,
            source_title=existing.source_title,
            text=existing.text,
            effective_date=existing.effective_date,
            approved_knowledge=existing.approved_knowledge,
            disabled=True,
        )
        self.documents[(tenant_id, source_document_id)] = disabled
        return disabled

    async def list_documents_for_retrieval(self, tenant_id: str) -> list[KnowledgeDocumentRecord]:
        return [
            document for document in await self.list_documents(tenant_id) if not document.disabled
        ]

    async def record_reindex(
        self,
        tenant_id: str,
        actor_id: str,
    ) -> ReindexRecord:
        active_documents = await self.list_documents_for_retrieval(tenant_id)
        record = ReindexRecord(
            tenant_id=tenant_id,
            actor_id=actor_id,
            reindexed_at=datetime.now(tz=UTC),
            corpus_version="corpus-v" + str(len(self.reindex_records) + 1),
            index_schema_version=INDEX_SCHEMA_VERSION,
            active_document_count=len(active_documents),
        )
        self.reindex_records.append(record)
        return record


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
    "InMemoryKnowledgeAdminStore",
    "IndexedKnowledgeChunk",
    "InMemoryKnowledgeIndex",
    "KnowledgeDocumentRecord",
    "KnowledgeIngestionPipeline",
    "ReindexRecord",
]


def _looks_like_customer_transcript(text: str) -> bool:
    lowered = text.lower()
    return "customer:" in lowered or "agent:" in lowered or "transcript" in lowered
