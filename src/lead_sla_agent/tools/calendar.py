"""Calendar provider adapter interfaces and fakes."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from lead_sla_agent.config import Settings


@dataclass(frozen=True)
class CalendarSlot:
    slot_id: str
    starts_at: datetime
    looked_up_at: datetime


@dataclass(frozen=True)
class BookingResult:
    booking_id: str
    status: str
    failure_reason: str | None = None
    idempotency_key: str | None = None


class BookingRejected(ValueError):
    """Raised when booking safety preconditions are not met."""


class CalendarHTTPResponse(Protocol):
    status_code: int

    def json(self) -> dict[str, Any]:
        """Return a decoded provider response body."""


class CalendarHTTPClient(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> Awaitable[CalendarHTTPResponse]:
        """Fetch provider slots."""

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, str],
        timeout: float,
    ) -> Awaitable[CalendarHTTPResponse]:
        """Create a provider booking."""


class FakeCalendarAdapter:
    def __init__(self, freshness_window: timedelta = timedelta(minutes=5)) -> None:
        self.freshness_window = freshness_window
        self.lookups: dict[str, CalendarSlot] = {}

    async def lookup_available_slots(self) -> list[CalendarSlot]:
        slot = CalendarSlot(
            slot_id="slot-1",
            starts_at=datetime.now(tz=UTC) + timedelta(days=1),
            looked_up_at=datetime.now(tz=UTC),
        )
        self.lookups[slot.slot_id] = slot
        return [slot]

    async def book_slot(self, slot_id: str, accepted: bool) -> BookingResult:
        slot = self.lookups.get(slot_id)
        now = datetime.now(tz=UTC)
        if slot is None or now - slot.looked_up_at > self.freshness_window:
            raise BookingRejected("fresh slot lookup is required before booking")
        if not accepted:
            raise BookingRejected("explicit customer acceptance is required before booking")
        return BookingResult(booking_id="booking-" + str(uuid.uuid4()), status="booked")


class CalendarProviderAdapter:
    """Calendar provider adapter with fakeable HTTP transport."""

    def __init__(
        self,
        api_token: str,
        api_url: str,
        http_client: CalendarHTTPClient,
        freshness_window: timedelta = timedelta(minutes=5),
        timeout_seconds: float = 10,
    ) -> None:
        self.api_token = api_token
        self.api_url = api_url.rstrip("/")
        self.http_client = http_client
        self.freshness_window = freshness_window
        self.timeout_seconds = timeout_seconds
        self.lookups: dict[str, CalendarSlot] = {}
        self.bookings_by_key: dict[str, BookingResult] = {}

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        http_client: CalendarHTTPClient,
    ) -> CalendarProviderAdapter:
        """Build the adapter from calendar-specific settings only."""
        return cls(
            api_token=settings.calendar_api_token,
            api_url=settings.calendar_api_url,
            http_client=http_client,
        )

    async def lookup_available_slots(self) -> list[CalendarSlot]:
        response = await self.http_client.get(
            self.api_url + "/slots",
            headers={"authorization": "Bearer " + self.api_token},
            timeout=self.timeout_seconds,
        )
        body = response.json()
        looked_up_at = datetime.now(tz=UTC)
        slots = [
            CalendarSlot(
                slot_id=str(raw_slot["slot_id"]),
                starts_at=datetime.fromisoformat(str(raw_slot["starts_at"])),
                looked_up_at=looked_up_at,
            )
            for raw_slot in body.get("slots", [])
        ]
        self.lookups.update({slot.slot_id: slot for slot in slots})
        return slots

    async def book_slot(
        self,
        slot_id: str,
        accepted: bool,
        idempotency_key: str | None = None,
    ) -> BookingResult:
        slot = self.lookups.get(slot_id)
        now = datetime.now(tz=UTC)
        if slot is None or now - slot.looked_up_at > self.freshness_window:
            raise BookingRejected("fresh slot lookup is required before booking")
        if not accepted:
            raise BookingRejected("explicit customer acceptance is required before booking")
        if not idempotency_key:
            raise BookingRejected("idempotency_key is required before booking")
        existing = self.bookings_by_key.get(idempotency_key)
        if existing is not None:
            return existing

        try:
            response = await self.http_client.post(
                self.api_url + "/bookings",
                headers={
                    "authorization": "Bearer " + self.api_token,
                    "idempotency-key": idempotency_key,
                },
                json={"slot_id": slot_id},
                timeout=self.timeout_seconds,
            )
        except TimeoutError:
            return BookingResult(
                booking_id="",
                status="human_review_required",
                failure_reason="provider_timeout",
                idempotency_key=idempotency_key,
            )

        body = response.json()
        result = BookingResult(
            booking_id=str(body.get("booking_id", "")),
            status=str(body.get("status", "booked")),
            failure_reason=None,
            idempotency_key=idempotency_key,
        )
        self.bookings_by_key[idempotency_key] = result
        return result
