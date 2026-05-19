"""Operator JSON API."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from lead_sla_agent.operator.auth import OperatorPrincipal, require_operator
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

router = APIRouter(prefix="/operator", tags=["operator"])


class ApprovalRequest(BaseModel):
    original_draft: str
    final_message: str
    reason_code: str


class OutcomeRequest(BaseModel):
    lead_id: str
    label: str
    labeled_on: date


def review_store(request: Request) -> HumanReviewTaskStore:
    if not hasattr(request.app.state, "review_store"):
        request.app.state.review_store = HumanReviewTaskStore()
    return request.app.state.review_store


def outcome_store(request: Request) -> OutcomeStore:
    if not hasattr(request.app.state, "outcome_store"):
        request.app.state.outcome_store = OutcomeStore()
    return request.app.state.outcome_store


RequireOperator = Depends(require_operator)
ReviewStore = Depends(review_store)
OutcomeStoreDependency = Depends(outcome_store)


@router.get("/reviews")
async def list_review_tasks(
    principal: OperatorPrincipal = RequireOperator,
    store: HumanReviewTaskStore = ReviewStore,
) -> dict[str, list[dict[str, Any]]]:
    return {"tasks": await store.list_tasks(principal.tenant_id)}


@router.post("/reviews/{task_id}/approve")
async def approve_reply(
    task_id: str,
    payload: ApprovalRequest,
    principal: OperatorPrincipal = RequireOperator,
    store: HumanReviewTaskStore = ReviewStore,
) -> dict[str, Any]:
    return await store.approve_reply(
        task_id=task_id,
        actor_id=principal.actor_id,
        original_draft=payload.original_draft,
        final_message=payload.final_message,
        reason_code=payload.reason_code,
    )


@router.post("/outcomes")
async def add_outcome_label(
    payload: OutcomeRequest,
    principal: OperatorPrincipal = RequireOperator,
    store: OutcomeStore = OutcomeStoreDependency,
) -> dict[str, Any]:
    return await store.add_label(
        tenant_id=principal.tenant_id,
        lead_id=payload.lead_id,
        label=payload.label,
        labeled_on=payload.labeled_on,
    )


@router.get("/outcomes")
async def query_outcome_labels(
    start_date: date,
    end_date: date,
    principal: OperatorPrincipal = RequireOperator,
    store: OutcomeStore = OutcomeStoreDependency,
) -> dict[str, list[dict[str, Any]]]:
    return {"labels": await store.query_labels(principal.tenant_id, start_date, end_date)}
