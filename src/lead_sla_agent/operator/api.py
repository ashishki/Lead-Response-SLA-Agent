"""Operator JSON API."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from lead_sla_agent.api.rate_limit import enforce_operator_rate_limit
from lead_sla_agent.operator.analytics import PilotAnalyticsStore
from lead_sla_agent.operator.auth import OperatorPrincipal, require_operator
from lead_sla_agent.operator.outcomes import OutcomeStore
from lead_sla_agent.operator.review_queue import HumanReviewTaskStore

router = APIRouter(
    prefix="/operator",
    tags=["operator"],
    dependencies=[Depends(enforce_operator_rate_limit)],
)


class ApprovalRequest(BaseModel):
    original_draft: str
    final_message: str
    reason_code: str


class NoSendRequest(BaseModel):
    original_draft: str
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


def analytics_store(request: Request) -> PilotAnalyticsStore:
    if not hasattr(request.app.state, "analytics_store"):
        request.app.state.analytics_store = PilotAnalyticsStore()
    return request.app.state.analytics_store


RequireOperator = Depends(require_operator)
ReviewStore = Depends(review_store)
OutcomeStoreDependency = Depends(outcome_store)
AnalyticsStore = Depends(analytics_store)


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
        tenant_id=principal.tenant_id,
    )


@router.post("/reviews/{task_id}/no-send")
async def mark_no_send(
    task_id: str,
    payload: NoSendRequest,
    principal: OperatorPrincipal = RequireOperator,
    store: HumanReviewTaskStore = ReviewStore,
) -> dict[str, Any]:
    return await store.mark_no_send(
        task_id=task_id,
        actor_id=principal.actor_id,
        original_draft=payload.original_draft,
        reason_code=payload.reason_code,
        tenant_id=principal.tenant_id,
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


@router.get("/analytics/weekly")
async def weekly_analytics(
    start_date: date,
    end_date: date,
    principal: OperatorPrincipal = RequireOperator,
    store: PilotAnalyticsStore = AnalyticsStore,
) -> dict[str, Any]:
    return store.weekly_report_payload(
        tenant_id=principal.tenant_id,
        start_date=start_date,
        end_date=end_date,
    )
