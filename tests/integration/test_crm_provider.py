from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

import pytest

from lead_sla_agent.config import Settings
from lead_sla_agent.tools.crm import CRMProviderAdapter


@dataclass(frozen=True)
class FakeCRMResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class FakeCRMHTTPClient:
    def __init__(
        self,
        response: FakeCRMResponse,
        timeout_on_write: bool = False,
    ) -> None:
        self.response = response
        self.timeout_on_write = timeout_on_write
        self.requests: list[dict[str, Any]] = []

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> FakeCRMResponse:
        if self.timeout_on_write:
            raise TimeoutError
        self.requests.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return self.response


def test_crm_adapter_uses_provider_specific_settings_only() -> None:
    adapter = CRMProviderAdapter.from_settings(
        Settings(
            SECRET_KEY="unrelated-secret",
            CRM_API_TOKEN="test-crm-token",
            CRM_API_URL="https://crm.example.test",
        ),
        FakeCRMHTTPClient(FakeCRMResponse(200, {"record_id": "crm-1"})),
    )

    assert adapter.api_token == "test-crm-token"
    assert adapter.api_url == "https://crm.example.test"


@pytest.mark.asyncio
async def test_crm_adapter_create_update_is_idempotent_by_source_event_id() -> None:
    lead_id = uuid.uuid4()
    http_client = FakeCRMHTTPClient(
        FakeCRMResponse(200, {"record_id": "crm-record-1", "status": "upserted"})
    )
    adapter = CRMProviderAdapter(
        api_token="test-crm-token",
        api_url="https://crm.example.test",
        http_client=http_client,
    )

    first = await adapter.create_or_update_lead(
        lead_id,
        {"status": "new", "email": "private@example.test"},
        source_event_id="source-event-1",
    )
    second = await adapter.create_or_update_lead(
        lead_id,
        {"status": "qualified", "email": "private@example.test"},
        source_event_id="source-event-1",
    )

    assert first == second
    assert first.remote_record_id == "crm-record-1"
    assert first.idempotency_key == "source-event-1"
    assert len(http_client.requests) == 1
    assert http_client.requests[0]["headers"] == {
        "authorization": "Bearer test-crm-token",
        "idempotency-key": "source-event-1",
    }


@pytest.mark.asyncio
async def test_crm_adapter_create_update_is_idempotent_by_lead_id() -> None:
    lead_id = uuid.uuid4()
    http_client = FakeCRMHTTPClient(FakeCRMResponse(200, {"record_id": "crm-record-2"}))
    adapter = CRMProviderAdapter(
        api_token="test-crm-token",
        api_url="https://crm.example.test",
        http_client=http_client,
    )

    first = await adapter.create_or_update_lead(lead_id, {"status": "new"})
    second = await adapter.create_or_update_lead(lead_id, {"status": "qualified"})

    assert first == second
    assert first.idempotency_key == str(lead_id)
    assert len(http_client.requests) == 1


@pytest.mark.asyncio
async def test_crm_failure_records_audit_event_and_retry_path_without_raising() -> None:
    lead_id = uuid.uuid4()
    adapter = CRMProviderAdapter(
        api_token="test-crm-token",
        api_url="https://crm.example.test",
        http_client=FakeCRMHTTPClient(FakeCRMResponse(503, {"status": "failed"})),
    )

    result = await adapter.create_or_update_lead(
        lead_id,
        {"status": "new", "email": "private@example.test"},
        source_event_id="source-event-failure",
    )

    assert result.status == "retry_required"
    assert result.retry_required is True
    assert result.failure_reason == "provider_http_error"
    assert result.audit_event == {
        "event_type": "crm.write_failed",
        "lead_id": str(lead_id),
        "reason": "provider_http_error",
        "idempotency_key": "source-event-failure",
        "handoff": "retry_or_human_review",
    }
    assert "private@example.test" not in str(adapter.audit_events)
