"""PII redaction helpers for observability boundaries."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

PII_FIELD_NAMES = frozenset(
    {
        "booking_details",
        "chat_content",
        "email",
        "lead_notes",
        "message",
        "name",
        "phone",
        "provider_message_id",
        "provider_user_id",
        "raw_webhook_payload",
        "transcript_text",
    }
)

REDACTED_VALUE = "[redacted]"
HASHED_IDENTIFIER_FIELDS = frozenset(
    {
        "email",
        "phone",
        "provider_message_id",
        "provider_user_id",
    }
)


def redact_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    """Return a shallow copy with known PII fields redacted."""
    return scrub_pii(values)


def hash_identifier(value: str) -> str:
    """Return a stable one-way identifier for observability data."""
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def scrub_pii(value: Any) -> Any:
    """Recursively scrub known structured PII fields."""
    if isinstance(value, Mapping):
        scrubbed: dict[str, Any] = {}
        for key, nested_value in value.items():
            if key in HASHED_IDENTIFIER_FIELDS and nested_value is not None:
                scrubbed[key] = hash_identifier(str(nested_value))
            elif key in PII_FIELD_NAMES:
                scrubbed[key] = REDACTED_VALUE
            else:
                scrubbed[key] = scrub_pii(nested_value)
        return scrubbed

    if isinstance(value, list):
        return [scrub_pii(nested_value) for nested_value in value]

    if isinstance(value, tuple):
        return tuple(scrub_pii(nested_value) for nested_value in value)

    return value
