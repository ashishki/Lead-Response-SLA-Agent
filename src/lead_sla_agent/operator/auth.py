"""Operator API authentication helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import Header, HTTPException, status

from lead_sla_agent.config import get_settings

TOKEN_PREFIX = "lead-sla-v1"
ALLOWED_OPERATOR_ROLES = frozenset({"owner", "operator"})
OPERATOR_TEST_TOKEN = ""


@dataclass(frozen=True)
class OperatorPrincipal:
    actor_id: str
    tenant_id: str
    role: str = "operator"


def issue_operator_token(
    actor_id: str,
    tenant_id: str,
    role: str,
    expires_at: datetime | None = None,
    secret: str | None = None,
) -> str:
    payload = {
        "actor_id": actor_id,
        "tenant_id": tenant_id,
        "role": role,
        "expires_at": expires_at.isoformat() if expires_at is not None else None,
    }
    encoded_payload = _base64url_encode(json.dumps(payload, sort_keys=True).encode("utf-8"))
    signature = _sign(encoded_payload, secret or get_settings().operator_auth_secret)
    return f"{TOKEN_PREFIX}.{encoded_payload}.{signature}"


async def require_operator(
    authorization: str | None = Header(default=None),
) -> OperatorPrincipal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    principal = _decode_operator_token(authorization.removeprefix("Bearer ").strip())
    if principal.role not in ALLOWED_OPERATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return principal


def _decode_operator_token(token: str) -> OperatorPrincipal:
    try:
        prefix, encoded_payload, signature = token.split(".", maxsplit=2)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized"
        ) from None

    if prefix != TOKEN_PREFIX:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    expected_signature = _sign(encoded_payload, get_settings().operator_auth_secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    try:
        payload = json.loads(_base64url_decode(encoded_payload).decode("utf-8"))
        actor_id = str(payload["actor_id"])
        tenant_id = str(payload["tenant_id"])
        role = str(payload["role"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized"
        ) from None

    expires_at = payload.get("expires_at")
    if expires_at is not None:
        expires = datetime.fromisoformat(str(expires_at))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires <= datetime.now(tz=UTC):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    return OperatorPrincipal(actor_id=actor_id, tenant_id=tenant_id, role=role)


def _sign(encoded_payload: str, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(digest)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


OPERATOR_TEST_TOKEN = issue_operator_token("operator-1", "tenant-1", "operator")
