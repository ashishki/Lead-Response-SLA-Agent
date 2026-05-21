from __future__ import annotations

import logging

import pytest

from lead_sla_agent.observability.logging import (
    clear_correlation_id,
    get_correlation_id,
    get_logger,
    log_structured_event,
    set_correlation_id,
)


@pytest.fixture(autouse=True)
def clear_correlation_context() -> None:
    clear_correlation_id()


def test_structured_logs_include_required_context_and_latency(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = get_logger("lead_sla_agent.tests.structured")
    set_correlation_id("corr-test-1")

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_structured_event(
            logger,
            tenant_hash="tenant:abc123",
            component="provider",
            action="send_message",
            result="rate_limited",
            latency_ms=42.5,
            trace_id="trace-123",
            fields={"provider": "twilio_whatsapp", "failure_reason": "rate_limited"},
        )

    logged_text = caplog.text
    for required in (
        "corr-test-1",
        "tenant:abc123",
        "provider",
        "send_message",
        "rate_limited",
        "42.5",
        "trace-123",
    ):
        assert required in logged_text


def test_correlation_id_is_stable_within_context_and_generated_when_missing() -> None:
    assert get_correlation_id().startswith("corr-")
    generated = get_correlation_id()
    assert get_correlation_id() == generated

    set_correlation_id("corr-explicit")

    assert get_correlation_id() == "corr-explicit"


def test_structured_logs_redact_known_pii_and_secrets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = get_logger("lead_sla_agent.tests.redaction")
    set_correlation_id("corr-redaction")
    fields = {
        "email": "lead@example.test",
        "phone": "+15550101010",
        "customer_name": "Private Lead",
        "customer_address": "123 Main Street",
        "message": "Need service at lead@example.test or +15550101010",
        "provider_message_id": "provider-msg-123",
        "token": "secret-token-value",
    }

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_structured_event(
            logger,
            tenant_hash="tenant:abc123",
            component="webhook",
            action="accept",
            result="ok",
            fields=fields,
        )

    logged_text = caplog.text
    for forbidden in fields.values():
        assert forbidden not in logged_text
    assert "[redacted]" in logged_text
    assert "sha256:" in logged_text


def test_plain_string_pii_patterns_are_redacted_in_captured_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = get_logger("lead_sla_agent.tests.string-redaction")

    with caplog.at_level(logging.INFO, logger=logger.name):
        logger.info("customer said email lead@example.test phone +15550101010 should be called")

    assert "lead@example.test" not in caplog.text
    assert "+15550101010" not in caplog.text
    assert "[redacted]" in caplog.text
