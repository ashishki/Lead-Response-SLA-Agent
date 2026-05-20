from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from lead_sla_agent.config import Settings
from lead_sla_agent.observability.pii import REDACTED_VALUE
from lead_sla_agent.tools.executor import execute_tool_call
from lead_sla_agent.tools.messaging import (
    EmailMessagingAdapter,
    MessagingProviderError,
    email_tool_adapter,
)
from lead_sla_agent.tools.safety import HumanReviewQueue
from lead_sla_agent.tools.schemas import ToolCall


def test_email_adapter_uses_provider_specific_settings_only() -> None:
    adapter = EmailMessagingAdapter.from_settings(
        Settings(
            SECRET_KEY="unrelated-secret",
            WEBHOOK_SHARED_SECRET="unrelated-webhook-secret",
            EMAIL_API_KEY="test-email-key",
            EMAIL_SENDER="sender@example.test",
            EMAIL_API_URL="https://email.example.test/messages",
        ),
        FakeEmailHTTPClient(FakeProviderResponse(202, {"message_id": "provider-msg-1"})),
    )

    assert adapter.api_key == "test-email-key"
    assert adapter.sender == "sender@example.test"
    assert adapter.api_url == "https://email.example.test/messages"


@dataclass(frozen=True)
class FakeProviderResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class FakeEmailHTTPClient:
    def __init__(self, response: FakeProviderResponse) -> None:
        self.response = response
        self.requests: list[dict[str, Any]] = []

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, str],
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


@pytest.mark.asyncio
async def test_email_adapter_sends_with_idempotency_and_records_provider_result() -> None:
    http_client = FakeEmailHTTPClient(
        FakeProviderResponse(202, {"message_id": "provider-msg-1", "status": "sent"})
    )
    adapter = EmailMessagingAdapter.from_settings(
        Settings(
            EMAIL_API_KEY="test-email-key",
            EMAIL_SENDER="sender@example.test",
            EMAIL_API_URL="https://email.example.test/messages",
        ),
        http_client,
    )

    result = await adapter.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Hello private lead",
        idempotency_key="conversation-1:hash:email",
    )

    assert result.provider_message_id == "provider-msg-1"
    assert result.status == "sent"
    assert result.latency_ms >= 0
    assert result.failure_reason is None
    assert result.redacted_preview == REDACTED_VALUE
    assert result.idempotency_key == "conversation-1:hash:email"
    assert http_client.requests[0]["headers"] == {
        "authorization": "Bearer test-email-key",
        "idempotency-key": "conversation-1:hash:email",
    }


@pytest.mark.asyncio
async def test_email_adapter_records_provider_failure_reason() -> None:
    http_client = FakeEmailHTTPClient(FakeProviderResponse(503, {"status": "failed"}))
    adapter = EmailMessagingAdapter(
        api_key="test-email-key",
        sender="sender@example.test",
        api_url="https://email.example.test/messages",
        http_client=http_client,
    )

    result = await adapter.send_message(
        channel="email",
        recipient="lead@example.test",
        text="Hello private lead",
        idempotency_key="conversation-1:hash:email",
    )

    assert result.status == "failed"
    assert result.provider_message_id == ""
    assert result.failure_reason == "provider_http_error"


@pytest.mark.asyncio
async def test_email_adapter_rejects_missing_idempotency_key() -> None:
    adapter = EmailMessagingAdapter(
        api_key="test-email-key",
        sender="sender@example.test",
        api_url="https://email.example.test/messages",
        http_client=FakeEmailHTTPClient(FakeProviderResponse(202, {"message_id": "unused"})),
    )

    with pytest.raises(MessagingProviderError, match="idempotency_key is required"):
        await adapter.send_message(
            channel="email",
            recipient="lead@example.test",
            text="Hello private lead",
        )


@pytest.mark.asyncio
async def test_unsafe_message_routes_to_review_before_email_provider_execution() -> None:
    http_client = FakeEmailHTTPClient(
        FakeProviderResponse(202, {"message_id": "provider-msg-unsafe", "status": "sent"})
    )
    adapter = EmailMessagingAdapter(
        api_key="test-email-key",
        sender="sender@example.test",
        api_url="https://email.example.test/messages",
        http_client=http_client,
    )
    review_queue = HumanReviewQueue()

    result = await execute_tool_call(
        ToolCall(
            tool_name="send_message",
            arguments={
                "channel": "email",
                "recipient": "lead@example.test",
                "text": "We guarantee custom pricing",
                "unsafe_categories": ["pricing"],
            },
            idempotency_key="conversation-1:hash:email",
        ),
        email_tool_adapter(adapter),
        review_queue,
    )

    assert result["status"] == "queued"
    assert http_client.requests == []
    assert review_queue.tasks[0]["reason"] == "unsafe_message_send"
