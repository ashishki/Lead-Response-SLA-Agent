from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.operator.analytics import PilotAnalyticsStore, PilotLeadEvent
from lead_sla_agent.operator.auth import OPERATOR_TEST_TOKEN

AUTH_HEADERS = {"authorization": f"Bearer {OPERATOR_TEST_TOKEN}"}


@pytest.mark.asyncio
async def test_operator_weekly_analytics_reports_roi_metrics() -> None:
    app = create_app()
    app.state.analytics_store = PilotAnalyticsStore(_sample_events())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/operator/analytics/weekly?start_date=2026-05-01&end_date=2026-05-07",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    body = response.json()
    metrics = body["metrics"]
    assert metrics["lead_count"] == 4
    assert metrics["first_response_latency_p50_ms"] == 3000.0
    assert metrics["first_response_latency_p95_ms"] == 10000.0
    assert metrics["automation_success_count"] == 2
    assert metrics["automation_success_rate"] == 0.5
    assert metrics["human_review_count"] == 1
    assert metrics["human_review_rate"] == 0.25
    assert metrics["booked_labels"] == 1
    assert metrics["provider_send_failures"] == 1
    assert "Pilot Weekly Report" in body["weekly_report"]
    assert "Provider send failures: 1" in body["weekly_report"]


@pytest.mark.asyncio
async def test_operator_weekly_analytics_is_tenant_scoped() -> None:
    app = create_app()
    base = datetime(2026, 5, 3, 12, tzinfo=UTC)
    app.state.analytics_store = PilotAnalyticsStore(
        [
            PilotLeadEvent(
                tenant_id="tenant-1",
                lead_id="lead-1",
                inbound_at=base,
                first_response_at=base + timedelta(seconds=1),
                response_mode="automated",
                outcome_label="booked",
            ),
            PilotLeadEvent(
                tenant_id="tenant-2",
                lead_id="lead-2",
                inbound_at=base,
                first_response_at=base + timedelta(seconds=60),
                response_mode="automated",
                outcome_label="booked",
            ),
        ]
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/operator/analytics/weekly?start_date=2026-05-01&end_date=2026-05-07",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    metrics = response.json()["metrics"]
    assert metrics["tenant_id"] == "tenant-1"
    assert metrics["lead_count"] == 1
    assert metrics["first_response_latency_p95_ms"] == 1000.0


@pytest.mark.asyncio
async def test_operator_weekly_analytics_requires_auth() -> None:
    app = create_app()
    app.state.analytics_store = PilotAnalyticsStore(_sample_events())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/operator/analytics/weekly?start_date=2026-05-01&end_date=2026-05-07",
        )

    assert response.status_code == 401


def _sample_events() -> list[PilotLeadEvent]:
    base = datetime(2026, 5, 3, 12, tzinfo=UTC)
    return [
        PilotLeadEvent(
            tenant_id="tenant-1",
            lead_id="lead-1",
            inbound_at=base,
            first_response_at=base + timedelta(seconds=1),
            response_mode="automated",
            outcome_label="booked",
        ),
        PilotLeadEvent(
            tenant_id="tenant-1",
            lead_id="lead-2",
            inbound_at=base,
            first_response_at=base + timedelta(seconds=2),
            response_mode="automated",
            outcome_label="qualified_handoff",
        ),
        PilotLeadEvent(
            tenant_id="tenant-1",
            lead_id="lead-3",
            inbound_at=base,
            first_response_at=base + timedelta(seconds=10),
            response_mode="human_review",
            human_review_required=True,
        ),
        PilotLeadEvent(
            tenant_id="tenant-1",
            lead_id="lead-4",
            inbound_at=base,
            first_response_at=base + timedelta(seconds=4),
            response_mode="automated",
            provider_send_failed=True,
        ),
    ]
