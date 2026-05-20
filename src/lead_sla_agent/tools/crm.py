"""CRM/spreadsheet adapter interfaces and fakes."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Protocol

from lead_sla_agent.config import Settings


@dataclass(frozen=True)
class CRMWriteResult:
    remote_record_id: str
    status: str
    idempotency_key: str
    failure_reason: str | None = None
    retry_required: bool = False
    audit_event: dict[str, str] | None = None


class CRMHTTPResponse(Protocol):
    status_code: int

    def json(self) -> dict[str, Any]:
        """Return a decoded provider response body."""


class CRMHTTPClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> Awaitable[CRMHTTPResponse]:
        """Create or update a provider lead record."""


class FakeCRMAdapter:
    def __init__(self) -> None:
        self.records_by_key: dict[str, CRMWriteResult] = {}
        self.write_count = 0

    async def create_or_update_lead(
        self,
        lead_id: uuid.UUID,
        fields: dict[str, Any],
    ) -> CRMWriteResult:
        del fields
        idempotency_key = str(lead_id)
        existing = self.records_by_key.get(idempotency_key)
        if existing is not None:
            return existing

        self.write_count += 1
        result = CRMWriteResult(
            remote_record_id="crm-" + str(uuid.uuid4()),
            status="upserted",
            idempotency_key=idempotency_key,
        )
        self.records_by_key[idempotency_key] = result
        return result


class CRMProviderAdapter:
    """CRM/spreadsheet destination adapter with fakeable HTTP transport."""

    def __init__(
        self,
        api_token: str,
        api_url: str,
        http_client: CRMHTTPClient,
        timeout_seconds: float = 10,
    ) -> None:
        self.api_token = api_token
        self.api_url = api_url.rstrip("/")
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds
        self.records_by_key: dict[str, CRMWriteResult] = {}
        self.audit_events: list[dict[str, str]] = []

    @classmethod
    def from_settings(cls, settings: Settings, http_client: CRMHTTPClient) -> CRMProviderAdapter:
        """Build the adapter from CRM-specific settings only."""
        return cls(
            api_token=settings.crm_api_token,
            api_url=settings.crm_api_url,
            http_client=http_client,
        )

    async def create_or_update_lead(
        self,
        lead_id: uuid.UUID,
        fields: dict[str, Any],
        source_event_id: str | None = None,
    ) -> CRMWriteResult:
        idempotency_key = source_event_id or str(lead_id)
        existing = self.records_by_key.get(idempotency_key)
        if existing is not None:
            return existing

        try:
            response = await self.http_client.post(
                self.api_url + "/leads",
                headers={
                    "authorization": "Bearer " + self.api_token,
                    "idempotency-key": idempotency_key,
                },
                json={"lead_id": str(lead_id), "fields": fields},
                timeout=self.timeout_seconds,
            )
        except TimeoutError:
            return self._failure_result(lead_id, idempotency_key, "provider_timeout")

        if response.status_code >= 400:
            return self._failure_result(lead_id, idempotency_key, "provider_http_error")

        body = response.json()
        result = CRMWriteResult(
            remote_record_id=str(body.get("record_id", "")),
            status=str(body.get("status", "upserted")),
            idempotency_key=idempotency_key,
        )
        self.records_by_key[idempotency_key] = result
        return result

    def _failure_result(
        self,
        lead_id: uuid.UUID,
        idempotency_key: str,
        reason: str,
    ) -> CRMWriteResult:
        audit_event = {
            "event_type": "crm.write_failed",
            "lead_id": str(lead_id),
            "reason": reason,
            "idempotency_key": idempotency_key,
            "handoff": "retry_or_human_review",
        }
        self.audit_events.append(audit_event)
        return CRMWriteResult(
            remote_record_id="",
            status="retry_required",
            idempotency_key=idempotency_key,
            failure_reason=reason,
            retry_required=True,
            audit_event=audit_event,
        )
