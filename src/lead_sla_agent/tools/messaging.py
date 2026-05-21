"""Messaging provider adapter interfaces and fakes."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

from lead_sla_agent.config import Settings
from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.tools.safety import HumanReviewQueue

LIVE_MESSAGING_PROVIDER_BY_CHANNEL = {
    "email": "postmark_email",
    "whatsapp": "twilio_whatsapp",
    "telegram": "telegram_bot",
}


@dataclass(frozen=True)
class MessageSendResult:
    provider_message_id: str
    status: str
    latency_ms: float
    redacted_preview: str
    failure_reason: str | None = None
    idempotency_key: str | None = None
    provider: str = "fake"
    channel: str = "unknown"
    rate_limited: bool = False
    review_task_id: str | None = None


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
        json: dict[str, Any],
        timeout: float,
    ) -> Awaitable[HTTPResponse]:
        """Send a provider HTTP request."""


class MessagingAdapter(Protocol):
    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        """Send a customer message through a provider."""


class FakeMessagingAdapter:
    def __init__(self) -> None:
        self.sent_messages: list[MessageSendResult] = []

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        del recipient, text, metadata
        start = time.perf_counter()
        result = MessageSendResult(
            provider_message_id="fake-msg-" + str(uuid.uuid4()),
            status="sent",
            latency_ms=(time.perf_counter() - start) * 1000,
            redacted_preview=REDACTED_VALUE,
            idempotency_key=idempotency_key,
            provider="fake",
            channel=channel,
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
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        del metadata
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
                provider="email",
                channel=channel,
            )

        body = response.json()
        return MessageSendResult(
            provider_message_id=str(body.get("message_id", "")),
            status=str(body.get("status", "sent")),
            latency_ms=latency_ms,
            redacted_preview=REDACTED_VALUE,
            failure_reason=None,
            idempotency_key=idempotency_key,
            provider="email",
            channel=channel,
        )


class PostmarkEmailAdapter:
    """Postmark transactional email adapter with injectable HTTP transport."""

    provider = "postmark_email"

    def __init__(
        self,
        server_token: str,
        sender: str,
        message_stream: str,
        api_url: str,
        http_client: HTTPClient,
        timeout_seconds: float = 10,
    ) -> None:
        self.server_token = server_token
        self.sender = sender
        self.message_stream = message_stream
        self.api_url = api_url
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings, http_client: HTTPClient) -> PostmarkEmailAdapter:
        return cls(
            server_token=settings.postmark_server_token,
            sender=settings.postmark_sender,
            message_stream=settings.postmark_message_stream,
            api_url=settings.postmark_api_url,
            http_client=http_client,
        )

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        del metadata
        if channel != "email":
            raise MessagingProviderError("Postmark adapter only supports email channel")
        if not idempotency_key:
            raise MessagingProviderError("idempotency_key is required")

        start = time.perf_counter()
        response = await self.http_client.post(
            self.api_url,
            headers={
                "X-Postmark-Server-Token": self.server_token,
                "idempotency-key": idempotency_key,
            },
            json={
                "From": self.sender,
                "To": recipient,
                "TextBody": text,
                "MessageStream": self.message_stream,
            },
            timeout=self.timeout_seconds,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        body = response.json()
        if response.status_code == 429:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason="rate_limited",
                rate_limited=True,
            )
        if response.status_code >= 400:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason=str(body.get("Message", "provider_http_error")),
            )

        return MessageSendResult(
            provider_message_id=str(body.get("MessageID", body.get("message_id", ""))),
            status=str(body.get("status", "sent")),
            latency_ms=latency_ms,
            redacted_preview=REDACTED_VALUE,
            failure_reason=None,
            idempotency_key=idempotency_key,
            provider=self.provider,
            channel=channel,
        )


class TwilioWhatsAppAdapter:
    """Twilio WhatsApp adapter with explicit opt-in enforcement."""

    provider = "twilio_whatsapp"

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        api_url: str,
        http_client: HTTPClient,
        timeout_seconds: float = 10,
    ) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.api_url = api_url.rstrip("/")
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings, http_client: HTTPClient) -> TwilioWhatsAppAdapter:
        return cls(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.twilio_whatsapp_from,
            api_url=settings.twilio_api_url,
            http_client=http_client,
        )

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        metadata = metadata or {}
        if channel != "whatsapp":
            raise MessagingProviderError("Twilio WhatsApp adapter only supports whatsapp channel")
        if not idempotency_key:
            raise MessagingProviderError("idempotency_key is required")
        if metadata.get("opt_in") is not True:
            raise MessagingProviderError("whatsapp sends require explicit opt-in metadata")

        start = time.perf_counter()
        response = await self.http_client.post(
            f"{self.api_url}/Accounts/{self.account_sid}/Messages.json",
            headers={
                "authorization": "Basic " + self.auth_token,
                "idempotency-key": idempotency_key,
            },
            json={
                "From": self.from_number,
                "To": recipient,
                "Body": text,
            },
            timeout=self.timeout_seconds,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        body = response.json()
        if response.status_code == 429:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason="rate_limited",
                rate_limited=True,
            )
        if response.status_code >= 400:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason=str(body.get("message", "provider_http_error")),
            )

        return MessageSendResult(
            provider_message_id=str(body.get("sid", "")),
            status=str(body.get("status", "queued")),
            latency_ms=latency_ms,
            redacted_preview=REDACTED_VALUE,
            idempotency_key=idempotency_key,
            provider=self.provider,
            channel=channel,
        )


class TelegramBotAdapter:
    """Telegram Bot API adapter for known chat IDs."""

    provider = "telegram_bot"

    def __init__(
        self,
        bot_token: str,
        api_url: str,
        http_client: HTTPClient,
        timeout_seconds: float = 10,
    ) -> None:
        self.bot_token = bot_token
        self.api_url = api_url.rstrip("/")
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings, http_client: HTTPClient) -> TelegramBotAdapter:
        return cls(
            bot_token=settings.telegram_bot_token,
            api_url=settings.telegram_api_url,
            http_client=http_client,
        )

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageSendResult:
        metadata = metadata or {}
        if channel != "telegram":
            raise MessagingProviderError("Telegram adapter only supports telegram channel")
        if not idempotency_key:
            raise MessagingProviderError("idempotency_key is required")
        if not metadata.get("chat_initiated"):
            raise MessagingProviderError("telegram sends require a known user-initiated chat ID")

        start = time.perf_counter()
        response = await self.http_client.post(
            f"{self.api_url}/bot{self.bot_token}/sendMessage",
            headers={"idempotency-key": idempotency_key},
            json={"chat_id": recipient, "text": text},
            timeout=self.timeout_seconds,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        body = response.json()
        if response.status_code == 429:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason="rate_limited",
                rate_limited=True,
            )
        if response.status_code >= 400 or body.get("ok") is False:
            return _provider_failure(
                provider=self.provider,
                channel=channel,
                latency_ms=latency_ms,
                idempotency_key=idempotency_key,
                failure_reason=str(body.get("description", "provider_http_error")),
            )

        message = body.get("result", {})
        return MessageSendResult(
            provider_message_id="telegram:" + str(message.get("message_id", "")),
            status="sent",
            latency_ms=latency_ms,
            redacted_preview=REDACTED_VALUE,
            idempotency_key=idempotency_key,
            provider=self.provider,
            channel=channel,
        )


class PilotMessagingGateway:
    """Pilot outbound gateway that defaults every channel to human approval."""

    def __init__(
        self,
        adapters_by_channel: dict[str, MessagingAdapter],
        review_queue: HumanReviewQueue,
        require_human_approval: bool = True,
    ) -> None:
        self.adapters_by_channel = adapters_by_channel
        self.review_queue = review_queue
        self.require_human_approval = require_human_approval
        self._processed_idempotency_keys: set[str] = set()

    async def send_message(
        self,
        channel: str,
        recipient: str,
        text: str,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
        human_approved: bool = False,
    ) -> MessageSendResult:
        if not idempotency_key:
            raise MessagingProviderError("idempotency_key is required")
        if idempotency_key in self._processed_idempotency_keys:
            return MessageSendResult(
                provider_message_id="",
                status="duplicate",
                latency_ms=0,
                redacted_preview=REDACTED_VALUE,
                idempotency_key=idempotency_key,
                provider=LIVE_MESSAGING_PROVIDER_BY_CHANNEL.get(channel, "unknown"),
                channel=channel,
            )
        self._processed_idempotency_keys.add(idempotency_key)

        if self.require_human_approval and not human_approved:
            task = await self.review_queue.create_task(
                {
                    "reason": "pilot_outbound_requires_human_approval",
                    "channel": channel,
                    "provider": LIVE_MESSAGING_PROVIDER_BY_CHANNEL.get(channel, "unknown"),
                    "idempotency_key": idempotency_key,
                }
            )
            return MessageSendResult(
                provider_message_id="",
                status="queued",
                latency_ms=0,
                redacted_preview=REDACTED_VALUE,
                failure_reason="human_approval_required",
                idempotency_key=idempotency_key,
                provider=LIVE_MESSAGING_PROVIDER_BY_CHANNEL.get(channel, "unknown"),
                channel=channel,
                review_task_id=str(task["task_id"]),
            )

        try:
            adapter = self.adapters_by_channel[channel]
        except KeyError:
            raise MessagingProviderError("unsupported messaging channel") from None
        return await adapter.send_message(
            channel=channel,
            recipient=recipient,
            text=text,
            idempotency_key=idempotency_key,
            metadata=metadata,
        )


def build_live_messaging_adapters(
    settings: Settings,
    http_client: HTTPClient,
) -> dict[str, MessagingAdapter]:
    return {
        "email": PostmarkEmailAdapter.from_settings(settings, http_client),
        "whatsapp": TwilioWhatsAppAdapter.from_settings(settings, http_client),
        "telegram": TelegramBotAdapter.from_settings(settings, http_client),
    }


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


def _provider_failure(
    provider: str,
    channel: str,
    latency_ms: float,
    idempotency_key: str,
    failure_reason: str,
    rate_limited: bool = False,
) -> MessageSendResult:
    return MessageSendResult(
        provider_message_id="",
        status="rate_limited" if rate_limited else "failed",
        latency_ms=latency_ms,
        redacted_preview=REDACTED_VALUE,
        failure_reason=failure_reason,
        idempotency_key=idempotency_key,
        provider=provider,
        channel=channel,
        rate_limited=rate_limited,
    )
