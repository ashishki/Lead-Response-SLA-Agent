from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from lead_sla_agent.config import Settings
from lead_sla_agent.tools.calendar import BookingRejected, CalendarProviderAdapter


@dataclass(frozen=True)
class FakeCalendarResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class FakeCalendarHTTPClient:
    def __init__(
        self,
        slot_response: FakeCalendarResponse,
        booking_response: FakeCalendarResponse | None = None,
        timeout_on_booking: bool = False,
    ) -> None:
        self.slot_response = slot_response
        self.booking_response = booking_response or FakeCalendarResponse(
            201,
            {"booking_id": "booking-1", "status": "booked"},
        )
        self.timeout_on_booking = timeout_on_booking
        self.get_requests: list[dict[str, Any]] = []
        self.post_requests: list[dict[str, Any]] = []

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> FakeCalendarResponse:
        self.get_requests.append({"url": url, "headers": headers, "timeout": timeout})
        return self.slot_response

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, str],
        timeout: float,
    ) -> FakeCalendarResponse:
        if self.timeout_on_booking:
            raise TimeoutError
        self.post_requests.append(
            {"url": url, "headers": headers, "json": json, "timeout": timeout}
        )
        return self.booking_response


def _slot_response(slot_id: str = "slot-1") -> FakeCalendarResponse:
    return FakeCalendarResponse(
        200,
        {
            "slots": [
                {
                    "slot_id": slot_id,
                    "starts_at": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                }
            ]
        },
    )


@pytest.mark.asyncio
async def test_calendar_adapter_rejects_booking_without_fresh_lookup() -> None:
    adapter = CalendarProviderAdapter(
        api_token="test-calendar-token",
        api_url="https://calendar.example.test",
        http_client=FakeCalendarHTTPClient(_slot_response()),
    )

    with pytest.raises(BookingRejected, match="fresh slot lookup is required"):
        await adapter.book_slot("slot-1", accepted=True, idempotency_key="lead-1:slot-1")


@pytest.mark.asyncio
async def test_calendar_adapter_rejects_booking_without_customer_acceptance() -> None:
    adapter = CalendarProviderAdapter(
        api_token="test-calendar-token",
        api_url="https://calendar.example.test",
        http_client=FakeCalendarHTTPClient(_slot_response()),
    )
    slots = await adapter.lookup_available_slots()

    with pytest.raises(BookingRejected, match="explicit customer acceptance is required"):
        await adapter.book_slot(slots[0].slot_id, accepted=False, idempotency_key="lead-1:slot-1")


@pytest.mark.asyncio
async def test_calendar_adapter_books_idempotently_after_fresh_lookup() -> None:
    http_client = FakeCalendarHTTPClient(_slot_response())
    adapter = CalendarProviderAdapter.from_settings(
        Settings(
            CALENDAR_API_TOKEN="test-calendar-token",
            CALENDAR_API_URL="https://calendar.example.test",
        ),
        http_client,
    )
    slots = await adapter.lookup_available_slots()

    first = await adapter.book_slot(
        slots[0].slot_id,
        accepted=True,
        idempotency_key="lead-1:slot-1",
    )
    second = await adapter.book_slot(
        slots[0].slot_id,
        accepted=True,
        idempotency_key="lead-1:slot-1",
    )

    assert first == second
    assert first.status == "booked"
    assert first.booking_id == "booking-1"
    assert first.idempotency_key == "lead-1:slot-1"
    assert len(http_client.post_requests) == 1
    assert http_client.post_requests[0]["headers"] == {
        "authorization": "Bearer test-calendar-token",
        "idempotency-key": "lead-1:slot-1",
    }


@pytest.mark.asyncio
async def test_calendar_provider_timeout_returns_human_review_fallback() -> None:
    adapter = CalendarProviderAdapter(
        api_token="test-calendar-token",
        api_url="https://calendar.example.test",
        http_client=FakeCalendarHTTPClient(_slot_response(), timeout_on_booking=True),
    )
    slots = await adapter.lookup_available_slots()

    result = await adapter.book_slot(
        slots[0].slot_id,
        accepted=True,
        idempotency_key="lead-1:slot-1",
    )

    assert result.status == "human_review_required"
    assert result.failure_reason == "provider_timeout"
    assert result.idempotency_key == "lead-1:slot-1"
