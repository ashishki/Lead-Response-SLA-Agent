"""Messaging provider adapter interfaces and fakes."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

from lead_sla_agent.config import Settings
from lead_sla_agent.observability.pii import REDACTED_VALUE


@dataclass(frozen=True)
class MessageSendResult:
    provider_message_id: str
    status: str
    latency_ms: float
    redacted_preview: str
    failure_reason: str | None = None
    idempotency_key: str | None = None


class MessagingProviderError(ValueError):
    """Raised when a messaging provider call violates adapter requirements."""


class HTTPResponse(Protocol):
    status_code: int

    def json(self) -> dict[str, Any]:
        """Return a decoded provider response body."""


class HTTPClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, str],
        timeout: float,
    ) -> Awaitable[HTTPResponse]:
        """Send a provider HTTP request."""


class FakeMessagingAdapter:
    def __init__(self) -> None:
        self.sent_messages: list[MessageSendResult] = []

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
    ) -> MessageSendResult:
        del channel, recipient, text
        start = time.perf_counter()
        result = MessageSendResult(
            provider_message_id="fake-msg-" + str(uuid.uuid4()),
            status="sent",
            latency_ms=(time.perf_counter() - start) * 1000,
            redacted_preview=REDACTED_VALUE,
            idempotency_key=idempotency_key,
        )
        self.sent_messages.append(result)
        return result


class EmailMessagingAdapter:
    """Email provider adapter with injectable HTTP transport for tests."""

    def __init__(
        self,
        api_key: str,
        sender: str,
        api_url: str,
        http_client: HTTPClient,
        timeout_seconds: float = 10,
    ) -> None:
        self.api_key = api_key
        self.sender = sender
        self.api_url = api_url
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings, http_client: HTTPClient) -> EmailMessagingAdapter:
        """Build the adapter from email-specific settings only."""
        return cls(
            api_key=settings.email_api_key,
            sender=settings.email_sender,
            api_url=settings.email_api_url,
            http_client=http_client,
        )

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
    ) -> MessageSendResult:
        if channel != "email":
            raise MessagingProviderError("email adapter only supports email channel")
        if not idempotency_key:
            raise MessagingProviderError("idempotency_key is required")

        start = time.perf_counter()
        response = await self.http_client.post(
            self.api_url,
            headers={
                "authorization": "Bearer " + self.api_key,
                "idempotency-key": idempotency_key,
            },
            json={
                "from": self.sender,
                "to": recipient,
                "text": text,
            },
            timeout=self.timeout_seconds,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        if response.status_code >= 400:
            return MessageSendResult(
                provider_message_id="",
                status="failed",
                latency_ms=latency_ms,
                redacted_preview=REDACTED_VALUE,
                failure_reason="provider_http_error",
                idempotency_key=idempotency_key,
            )

        body = response.json()
        return MessageSendResult(
            provider_message_id=str(body.get("message_id", "")),
            status=str(body.get("status", "sent")),
            latency_ms=latency_ms,
            redacted_preview=REDACTED_VALUE,
            failure_reason=None,
            idempotency_key=idempotency_key,
        )


def email_tool_adapter(
    adapter: EmailMessagingAdapter,
) -> Callable[[Any], Awaitable[dict[str, Any]]]:
    """Wrap an email adapter for tool executor tests."""

    async def _send(tool_call: Any) -> dict[str, Any]:
        result = await adapter.send_message(
            channel=str(tool_call.arguments["channel"]),
            recipient=str(tool_call.arguments["recipient"]),
            text=str(tool_call.arguments["text"]),
            idempotency_key=tool_call.idempotency_key,
        )
        return {
            "provider_message_id": result.provider_message_id,
            "status": result.status,
            "latency_ms": result.latency_ms,
            "failure_reason": result.failure_reason,
        }

    return _send
