"""Webhook signature helpers."""

from __future__ import annotations

import hashlib
import hmac

SIGNATURE_HEADER = "X-Lead-SLA-Signature"
SIGNATURE_PREFIX = "sha256="


def build_signature(raw_body: bytes, shared_secret: str) -> str:
    """Build the canonical HMAC signature for a webhook body."""
    digest = hmac.new(shared_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"{SIGNATURE_PREFIX}{digest}"


def verify_signature(raw_body: bytes, signature: str | None, shared_secret: str) -> bool:
    """Verify a webhook signature without leaking timing information."""
    if not signature:
        return False

    expected_signature = build_signature(raw_body, shared_secret)
    return hmac.compare_digest(signature, expected_signature)
