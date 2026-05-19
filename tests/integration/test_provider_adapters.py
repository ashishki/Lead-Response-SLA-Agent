from __future__ import annotations

import uuid

import pytest

from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.tools.calendar import BookingRejected, FakeCalendarAdapter
from lead_sla_agent.tools.crm import FakeCRMAdapter
from lead_sla_agent.tools.messaging import FakeMessagingAdapter


@pytest.mark.asyncio
async def test_fake_messaging_adapter_records_send_result() -> None:
    adapter = FakeMessagingAdapter()

    result = await adapter.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Hello Test Lead",
    )

    assert result.provider_message_id.startswith("fake-msg-")
    assert result.status == "sent"
    assert result.latency_ms >= 0
    assert result.redacted_preview == REDACTED_VALUE
    assert adapter.sent_messages == [result]


@pytest.mark.asyncio
async def test_booking_requires_fresh_slot_lookup() -> None:
    adapter = FakeCalendarAdapter()

    with pytest.raises(BookingRejected, match="fresh slot lookup is required"):
        await adapter.book_slot("slot-1", accepted=True)

    slots = await adapter.lookup_available_slots()
    result = await adapter.book_slot(slots[0].slot_id, accepted=True)

    assert result.status == "booked"


@pytest.mark.asyncio
async def test_crm_write_is_idempotent() -> None:
    adapter = FakeCRMAdapter()
    lead_id = uuid.uuid4()

    first = await adapter.create_or_update_lead(lead_id, {"status": "new"})
    second = await adapter.create_or_update_lead(lead_id, {"status": "qualified"})

    assert first == second
    assert adapter.write_count == 1
