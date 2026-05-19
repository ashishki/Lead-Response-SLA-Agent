"""PII-safe logging helpers."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from lead_sla_agent.observability.pii import scrub_pii


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
