"""Tenant-scoped query-time retrieval."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field

from lead_sla_agent.retrieval.evidence import EvidenceBlock, HumanReviewTask, RetrievalResult
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeIndex

TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "i",
    "is",
    "me",
    "my",
    "the",
    "to",
    "we",
    "what",
    "you",
}


@dataclass
class InMemoryHumanReviewSink:
    tasks: list[HumanReviewTask] = field(default_factory=list)

    async def create(self, task: HumanReviewTask) -> None:
        if task not in self.tasks:
            self.tasks.append(task)


class RetrievalQueryService:
    """Retrieve tenant-scoped evidence or return insufficient evidence."""

    def __init__(
        self,
        index: InMemoryKnowledgeIndex,
        review_sink: InMemoryHumanReviewSink,
        min_score: float = 0.1,
    ) -> None:
        self.index = index
        self.review_sink = review_sink
        self.min_score = min_score

    async def retrieve(
        self,
        tenant_id: uuid.UUID,
        query_text: str,
        limit: int = 5,
    ) -> RetrievalResult:
        query_terms = _tokenize(query_text)
        candidates: list[EvidenceBlock] = []
        for indexed_chunk in self.index.list_chunks():
            chunk = indexed_chunk.chunk
            if chunk.tenant_id != tenant_id:
                continue
            score = _score_terms(query_terms, _tokenize(chunk.content))
            if score < self.min_score:
                continue
            candidates.append(
                EvidenceBlock(
                    tenant_id=tenant_id,
                    source_document_id=chunk.source_document_id,
                    source_title=chunk.source_title,
                    chunk_ordinal=chunk.chunk_ordinal,
                    content=chunk.content,
                    score=score,
                )
            )

        candidates.sort(key=lambda candidate: candidate.score, reverse=True)
        top_score = candidates[0].score if candidates else 0
        evidence = [candidate for candidate in candidates if candidate.score == top_score][:limit]
        if evidence:
            return RetrievalResult(status="evidence", evidence=evidence, answer_text=None)

        task = HumanReviewTask(
            tenant_id=tenant_id,
            reason="insufficient_evidence",
            query_hash=hashlib.sha256(query_text.encode("utf-8")).hexdigest(),
        )
        await self.review_sink.create(task)
        return RetrievalResult(
            status="insufficient_evidence",
            evidence=[],
            answer_text=None,
            human_review_task=task,
        )


def _tokenize(text: str) -> set[str]:
    return {token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS}


def _score_terms(query_terms: set[str], content_terms: set[str]) -> float:
    if not query_terms:
        return 0
    return len(query_terms & content_terms) / len(query_terms)
