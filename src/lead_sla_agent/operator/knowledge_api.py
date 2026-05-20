"""Operator knowledge administration API."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from lead_sla_agent.operator.auth import OperatorPrincipal, require_operator
from lead_sla_agent.retrieval.ingestion import InMemoryKnowledgeAdminStore

router = APIRouter(prefix="/operator/knowledge", tags=["operator-knowledge"])


class KnowledgeUploadRequest(BaseModel):
    source_document_id: str = Field(min_length=1, max_length=255)
    source_title: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1)
    effective_date: date
    approved_knowledge: bool = False


def knowledge_store(request: Request) -> InMemoryKnowledgeAdminStore:
    if not hasattr(request.app.state, "knowledge_store"):
        request.app.state.knowledge_store = InMemoryKnowledgeAdminStore()
    return request.app.state.knowledge_store


RequireOperator = Depends(require_operator)
KnowledgeStore = Depends(knowledge_store)


@router.post("")
async def upload_knowledge_document(
    payload: KnowledgeUploadRequest,
    principal: OperatorPrincipal = RequireOperator,
    store: InMemoryKnowledgeAdminStore = KnowledgeStore,
) -> dict[str, Any]:
    try:
        record = await store.upload_document(
            tenant_id=principal.tenant_id,
            source_document_id=payload.source_document_id,
            source_title=payload.source_title,
            text=payload.text,
            effective_date=payload.effective_date,
            approved_knowledge=payload.approved_knowledge,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _record_dict(record)


@router.get("")
async def list_knowledge_documents(
    principal: OperatorPrincipal = RequireOperator,
    store: InMemoryKnowledgeAdminStore = KnowledgeStore,
) -> dict[str, list[dict[str, Any]]]:
    return {
        "documents": [
            _record_dict(record) for record in await store.list_documents(principal.tenant_id)
        ]
    }


@router.post("/{source_document_id}/disable")
async def disable_knowledge_document(
    source_document_id: str,
    principal: OperatorPrincipal = RequireOperator,
    store: InMemoryKnowledgeAdminStore = KnowledgeStore,
) -> dict[str, Any]:
    record = await store.disable_document(principal.tenant_id, source_document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document not found")
    return _record_dict(record)


@router.post("/reindex")
async def reindex_knowledge_documents(
    principal: OperatorPrincipal = RequireOperator,
    store: InMemoryKnowledgeAdminStore = KnowledgeStore,
) -> dict[str, Any]:
    record = await store.record_reindex(
        tenant_id=principal.tenant_id,
        actor_id=principal.actor_id,
    )
    return {
        "tenant_id": record.tenant_id,
        "actor_id": record.actor_id,
        "reindexed_at": record.reindexed_at.isoformat(),
        "corpus_version": record.corpus_version,
        "index_schema_version": record.index_schema_version,
        "active_document_count": record.active_document_count,
    }


def _record_dict(record: Any) -> dict[str, Any]:
    values = asdict(record)
    values["effective_date"] = record.effective_date.isoformat()
    return values
