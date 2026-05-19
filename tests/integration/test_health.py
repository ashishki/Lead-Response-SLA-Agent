from __future__ import annotations

import logging

import pytest
from httpx import ASGITransport, AsyncClient

from lead_sla_agent.api.app import create_app
from lead_sla_agent.observability.pii import PII_FIELD_NAMES


@pytest.mark.asyncio
async def test_health_returns_ok_without_pii(caplog: pytest.LogCaptureFixture) -> None:
    app = create_app()
    transport = ASGITransport(app=app)

    with caplog.at_level(logging.INFO):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert not (PII_FIELD_NAMES & set(response.json()))
    logged_text = "\n".join(record.getMessage() for record in caplog.records)
    assert not any(record.name.startswith("lead_sla_agent") for record in caplog.records)
    assert not any(field_name in logged_text for field_name in PII_FIELD_NAMES)


@pytest.mark.asyncio
async def test_health_reports_dependencies_without_pii() -> None:
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    body = response.json()
    assert response.status_code == 200
    assert body["dependencies"]["database"]["status"] == "ok"
    assert body["dependencies"]["redis"]["status"] == "ok"
    assert body["dependencies"]["retrieval"]["freshness"] == "fresh"
    assert not any(field_name in str(body) for field_name in PII_FIELD_NAMES)
