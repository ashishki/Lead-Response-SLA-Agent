from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

import pytest

from lead_sla_agent.config import PROVIDER_SECRET_NAMES_BY_ADAPTER, Settings
from lead_sla_agent.observability.metrics import metrics
from lead_sla_agent.tools.messaging import (
    LIVE_MESSAGING_PROVIDER_BY_CHANNEL,
    MessagingProviderError,
    PilotMessagingGateway,
    PostmarkEmailAdapter,
    TelegramBotAdapter,
    TwilioWhatsAppAdapter,
    build_live_messaging_adapters,
)
from lead_sla_agent.tools.safety import HumanReviewQueue
from lead_sla_agent.workers.retries import RetryState, record_provider_send_result


@dataclass(frozen=True)
class FakeProviderResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class RecordingHTTPClient:
    def __init__(self, response: FakeProviderResponse) -> None:
        self.response = response
        self.requests: list[dict[str, Any]] = []

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> FakeProviderResponse:
        self.requests.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return self.response


def test_live_provider_credentials_are_scoped_and_not_required_for_normal_settings() -> None:
    settings = Settings()
    adapters = build_live_messaging_adapters(
        settings,
        RecordingHTTPClient(FakeProviderResponse(202, {"MessageID": "unused"})),
    )

    assert set(adapters) == {"email", "whatsapp", "telegram"}
    assert LIVE_MESSAGING_PROVIDER_BY_CHANNEL == {
        "email": "postmark_email",
        "whatsapp": "twilio_whatsapp",
        "telegram": "telegram_bot",
    }
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["postmark_email"] == frozenset(
        {"POSTMARK_SERVER_TOKEN", "POSTMARK_SENDER", "POSTMARK_MESSAGE_STREAM"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["twilio_whatsapp"] == frozenset(
        {"TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"}
    )
    assert PROVIDER_SECRET_NAMES_BY_ADAPTER["telegram_bot"] == frozenset({"TELEGRAM_BOT_TOKEN"})


@pytest.mark.asyncio
async def test_postmark_email_records_provider_delivery_metadata() -> None:
    http_client = RecordingHTTPClient(
        FakeProviderResponse(200, {"MessageID": "postmark-msg-1", "status": "sent"})
    )
    adapter = PostmarkEmailAdapter(
        server_token="postmark-token",
        sender="leads@example.test",
        message_stream="outbound",
        api_url="https://api.postmarkapp.com/email",
        http_client=http_client,
    )

    result = await adapter.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Approved reply",
        idempotency_key="conversation:hash:email",
    )

    assert result.provider == "postmark_email"
    assert result.channel == "email"
    assert result.provider_message_id == "postmark-msg-1"
    assert result.status == "sent"
    assert result.failure_reason is None
    assert result.latency_ms >= 0
    assert http_client.requests[0]["headers"]["X-Postmark-Server-Token"] == "postmark-token"
    assert http_client.requests[0]["json"]["MessageStream"] == "outbound"


@pytest.mark.asyncio
async def test_twilio_whatsapp_requires_opt_in_and_records_rate_limit() -> None:
    adapter = TwilioWhatsAppAdapter(
        account_sid="sid",
        auth_token="auth-token",
        from_number="whatsapp:+15550000000",
        api_url="https://api.twilio.com/2010-04-01",
        http_client=RecordingHTTPClient(FakeProviderResponse(429, {"message": "too many"})),
    )

    with pytest.raises(MessagingProviderError, match="explicit opt-in"):
        await adapter.send_message(
            channel="whatsapp",
            recipient="whatsapp:+15551112222",
            text="Approved reply",
            idempotency_key="conversation:hash:whatsapp",
        )

    result = await adapter.send_message(
        channel="whatsapp",
        recipient="whatsapp:+15551112222",
        text="Approved reply",
        idempotency_key="conversation:hash:whatsapp",
        metadata={"opt_in": True},
    )

    assert result.provider == "twilio_whatsapp"
    assert result.channel == "whatsapp"
    assert result.status == "rate_limited"
    assert result.failure_reason == "rate_limited"
    assert result.rate_limited is True


@pytest.mark.asyncio
async def test_telegram_requires_user_initiated_chat_id_before_live_send() -> None:
    http_client = RecordingHTTPClient(
        FakeProviderResponse(200, {"ok": True, "result": {"message_id": 42}})
    )
    adapter = TelegramBotAdapter(
        bot_token="telegram-token",
        api_url="https://api.telegram.org",
        http_client=http_client,
    )

    with pytest.raises(MessagingProviderError, match="user-initiated chat ID"):
        await adapter.send_message(
            channel="telegram",
            recipient="12345",
            text="Approved reply",
            idempotency_key="conversation:hash:telegram",
        )

    result = await adapter.send_message(
        channel="telegram",
        recipient="12345",
        text="Approved reply",
        idempotency_key="conversation:hash:telegram",
        metadata={"chat_initiated": True},
    )

    assert result.provider == "telegram_bot"
    assert result.provider_message_id == "telegram:42"
    assert result.status == "sent"
    assert "/bottelegram-token/sendMessage" in http_client.requests[0]["url"]


@pytest.mark.asyncio
async def test_pilot_gateway_requires_human_approval_for_every_channel() -> None:
    review_queue = HumanReviewQueue()
    http_client = RecordingHTTPClient(
        FakeProviderResponse(200, {"MessageID": "postmark-msg-1", "status": "sent"})
    )
    gateway = PilotMessagingGateway(
        adapters_by_channel={
            "email": PostmarkEmailAdapter(
                server_token="postmark-token",
                sender="leads@example.test",
                message_stream="outbound",
                api_url="https://api.postmarkapp.com/email",
                http_client=http_client,
            )
        },
        review_queue=review_queue,
    )

    queued = await gateway.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Needs approval",
        idempotency_key="conversation:hash:email",
    )

    assert queued.status == "queued"
    assert queued.failure_reason == "human_approval_required"
    assert queued.provider == "postmark_email"
    assert queued.review_task_id == "review-1"
    assert review_queue.tasks[0]["reason"] == "pilot_outbound_requires_human_approval"
    assert http_client.requests == []

    duplicate = await gateway.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Needs approval",
        idempotency_key="conversation:hash:email",
        human_approved=True,
    )

    assert duplicate.status == "duplicate"
    assert http_client.requests == []


@pytest.mark.asyncio
async def test_approved_pilot_send_calls_provider_once() -> None:
    review_queue = HumanReviewQueue()
    http_client = RecordingHTTPClient(
        FakeProviderResponse(200, {"MessageID": "postmark-msg-1", "status": "sent"})
    )
    gateway = PilotMessagingGateway(
        adapters_by_channel={
            "email": PostmarkEmailAdapter(
                server_token="postmark-token",
                sender="leads@example.test",
                message_stream="outbound",
                api_url="https://api.postmarkapp.com/email",
                http_client=http_client,
            )
        },
        review_queue=review_queue,
    )

    sent = await gateway.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Approved reply",
        idempotency_key="conversation:approved:email",
        human_approved=True,
    )

    assert sent.status == "sent"
    assert sent.provider_message_id == "postmark-msg-1"
    assert len(http_client.requests) == 1
    assert review_queue.tasks == []


@pytest.mark.asyncio
async def test_provider_failure_creates_retry_then_handoff_without_duplicate_review() -> None:
    metrics.reset()
    review_tasks: list[tuple[uuid.UUID, str]] = []
    retry_state = RetryState(lead_id=uuid.uuid4(), max_attempts=2)
    result = await TwilioWhatsAppAdapter(
        account_sid="sid",
        auth_token="auth-token",
        from_number="whatsapp:+15550000000",
        api_url="https://api.twilio.com/2010-04-01",
        http_client=RecordingHTTPClient(FakeProviderResponse(429, {"message": "too many"})),
    ).send_message(
        channel="whatsapp",
        recipient="whatsapp:+15551112222",
        text="Approved reply",
        idempotency_key="conversation:hash:whatsapp",
        metadata={"opt_in": True},
    )

    async def create_review_task(lead_id: uuid.UUID, reason: str) -> None:
        review_tasks.append((lead_id, reason))

    assert await record_provider_send_result(retry_state, result, create_review_task) is False
    assert await record_provider_send_result(retry_state, result, create_review_task) is True
    assert await record_provider_send_result(retry_state, result, create_review_task) is False

    assert review_tasks == [(retry_state.lead_id, "provider_rate_limited")]
    assert metrics.counters["provider_send_failure_total"] == 2
