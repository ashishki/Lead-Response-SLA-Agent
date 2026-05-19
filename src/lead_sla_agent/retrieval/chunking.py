"""Heading-aware chunking for approved text knowledge."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import date

from lead_sla_agent.retrieval.documents import NormalizedKnowledgeDocument

INDEX_SCHEMA_VERSION = "rag-index-v1"
CHUNKING_STRATEGY = "markdown-heading-v1"
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(?P<title>.+)$")


@dataclass(frozen=True)
class KnowledgeChunkDraft:
    tenant_id: uuid.UUID
    source_document_id: str
    source_title: str
    effective_date: date
    content: str
    content_hash: str
    chunk_ordinal: int
    index_schema_version: str = INDEX_SCHEMA_VERSION


def chunk_markdown_document(document: NormalizedKnowledgeDocument) -> list[KnowledgeChunkDraft]:
    """Split markdown by headings and preserve source metadata on every chunk."""
    sections: list[list[str]] = []
    current_section: list[str] = []

    for line in document.text.splitlines():
        if HEADING_PATTERN.match(line) and current_section:
            sections.append(current_section)
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        sections.append(current_section)

    chunks: list[KnowledgeChunkDraft] = []
    for ordinal, section_lines in enumerate(sections):
        content = "\n".join(section_lines).strip()
        if not content:
            continue
        chunks.append(
            KnowledgeChunkDraft(
                tenant_id=document.ref.tenant_id,
                source_document_id=document.ref.source_document_id,
                source_title=document.ref.source_title,
                effective_date=document.ref.effective_date,
                content=content,
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                chunk_ordinal=ordinal,
            )
        )
    return chunks
