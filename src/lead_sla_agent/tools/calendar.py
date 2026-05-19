"""Calendar provider adapter interfaces and fakes."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class CalendarSlot:
    slot_id: str
    starts_at: datetime
    looked_up_at: datetime


@dataclass(frozen=True)
class BookingResult:
    booking_id: str
    status: str


class BookingRejected(ValueError):
    """Raised when booking safety preconditions are not met."""


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
        return BookingResult(booking_id=f"booking-{uuid.uuid4()}", status="booked")
