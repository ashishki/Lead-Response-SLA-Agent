"""Typed retrieval evidence results."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceBlock:
    tenant_id: uuid.UUID
    source_document_id: str
    source_title: str
    chunk_ordinal: int
    content: str
    score: float


@dataclass(frozen=True)
class HumanReviewTask:
    tenant_id: uuid.UUID
    reason: str
    query_hash: str


@dataclass(frozen=True)
class RetrievalResult:
    status: str
    evidence: list[EvidenceBlock] = field(default_factory=list)
    answer_text: str | None = None
    human_review_task: HumanReviewTask | None = None
