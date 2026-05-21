"""PII-safe logging helpers."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from lead_sla_agent.observability.pii import scrub_pii

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


@dataclass(frozen=True)
class StructuredLogEvent:
    correlation_id: str
    tenant_hash: str
    component: str
    action: str
    result: str
    latency_ms: float | None = None
    trace_id: str | None = None
    fields: Mapping[str, Any] | None = None

    def to_log_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "correlation_id": self.correlation_id,
            "tenant_hash": self.tenant_hash,
            "component": self.component,
            "action": self.action,
            "result": self.result,
        }
        if self.latency_ms is not None:
            record["latency_ms"] = self.latency_ms
        if self.trace_id is not None:
            record["trace_id"] = self.trace_id
        if self.fields:
            record.update(dict(self.fields))
        return scrub_pii(record)


class PIIRedactingFilter(logging.Filter):
    """Scrub structured log messages and arguments before emission."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = scrub_pii(record.msg)
        if isinstance(record.args, Mapping):
            record.args = scrub_pii(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(scrub_pii(value) for value in record.args)

        for key, value in list(record.__dict__.items()):
            if key not in logging.LogRecord(None, None, "", 0, "", (), None).__dict__:
                setattr(record, key, scrub_pii({key: value}).get(key, value))

        return True


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the PII redaction filter attached."""
    logger = logging.getLogger(name)
    has_redacting_filter = any(
        isinstance(existing_filter, PIIRedactingFilter) for existing_filter in logger.filters
    )
    if not has_redacting_filter:
        logger.addFilter(PIIRedactingFilter())
    return logger


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set and return the current request correlation ID."""
    value = correlation_id or "corr-" + uuid.uuid4().hex
    _correlation_id.set(value)
    return value


def get_correlation_id() -> str:
    """Return the active correlation ID, creating one when absent."""
    existing = _correlation_id.get()
    if existing is not None:
        return existing
    return set_correlation_id()


def clear_correlation_id() -> None:
    """Clear correlation context for tests and worker boundaries."""
    _correlation_id.set(None)


def log_structured_event(
    logger: logging.Logger,
    *,
    tenant_hash: str,
    component: str,
    action: str,
    result: str,
    latency_ms: float | None = None,
    trace_id: str | None = None,
    fields: Mapping[str, Any] | None = None,
    level: int = logging.INFO,
) -> StructuredLogEvent:
    """Emit a PII-scrubbed structured event and return the emitted payload."""
    event = StructuredLogEvent(
        correlation_id=get_correlation_id(),
        tenant_hash=tenant_hash,
        component=component,
        action=action,
        result=result,
        latency_ms=latency_ms,
        trace_id=trace_id,
        fields=fields,
    )
    payload = event.to_log_record()
    logger.log(level, "structured_event %s", payload)
    return event
