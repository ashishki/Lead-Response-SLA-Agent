"""Text-only retrieval document contracts."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class SourceDocumentRef:
    tenant_id: uuid.UUID
    source_document_id: str
    source_title: str
    effective_date: date


@dataclass(frozen=True)
class FetchedKnowledgeDocument:
    ref: SourceDocumentRef
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedKnowledgeDocument:
    ref: SourceDocumentRef
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


def normalize_text_document(document: FetchedKnowledgeDocument) -> NormalizedKnowledgeDocument:
    """Normalize approved source text without changing retrieval semantics."""
    normalized_lines = [line.rstrip() for line in document.text.strip().splitlines()]
    return NormalizedKnowledgeDocument(
        ref=document.ref,
        text="\n".join(normalized_lines).strip(),
        metadata=document.metadata,
    )
