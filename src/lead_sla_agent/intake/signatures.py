"""Webhook signature helpers."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping

SIGNATURE_HEADER = "X-Lead-SLA-Signature"
SIGNATURE_PREFIX = "sha256="
PROVIDER_HEADER = "X-Lead-SLA-Provider"
WHATSAPP_SIGNATURE_HEADER = "X-Hub-Signature-256"
TELEGRAM_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"


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


def build_provider_signature(provider: str, raw_body: bytes, shared_secret: str) -> str:
    """Build a provider-specific test signature."""
    if provider == "telegram":
        return shared_secret
    return build_signature(raw_body, shared_secret)


def verify_provider_signature(
    provider: str,
    raw_body: bytes,
    headers: Mapping[str, str],
    shared_secret: str,
) -> bool:
    """Verify the configured signature scheme for a named inbound provider."""
    normalized_provider = provider.lower()
    if normalized_provider == "email":
        return verify_signature(raw_body, headers.get(SIGNATURE_HEADER), shared_secret)
    if normalized_provider == "whatsapp":
        return verify_signature(raw_body, headers.get(WHATSAPP_SIGNATURE_HEADER), shared_secret)
    if normalized_provider == "telegram":
        token = headers.get(TELEGRAM_SECRET_HEADER)
        return token is not None and hmac.compare_digest(token, shared_secret)
    return False
