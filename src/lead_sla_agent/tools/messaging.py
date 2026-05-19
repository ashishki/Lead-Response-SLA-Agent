"""Messaging provider adapter interfaces and fakes."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from lead_sla_agent.observability.pii import REDACTED_VALUE


@dataclass(frozen=True)
class MessageSendResult:
    provider_message_id: str
    status: str
    latency_ms: float
    redacted_preview: str


class FakeMessagingAdapter:
    def __init__(self) -> None:
        self.sent_messages: list[MessageSendResult] = []

    async def send_message(self, channel: str, recipient: str, text: str) -> MessageSendResult:
        del channel, recipient, text
        start = time.perf_counter()
        result = MessageSendResult(
            provider_message_id=f"fake-msg-{uuid.uuid4()}",
            status="sent",
            latency_ms=(time.perf_counter() - start) * 1000,
            redacted_preview=REDACTED_VALUE,
        )
        self.sent_messages.append(result)
        return result
