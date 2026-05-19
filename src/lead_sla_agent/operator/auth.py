"""Operator API authentication helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException, status

OPERATOR_TEST_TOKEN = "test-operator-token"


@dataclass(frozen=True)
class OperatorPrincipal:
    actor_id: str
    tenant_id: str
    role: str = "operator"


async def require_operator(
    authorization: str | None = Header(default=None),
) -> OperatorPrincipal:
    if authorization != f"Bearer {OPERATOR_TEST_TOKEN}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    return OperatorPrincipal(actor_id="operator-1", tenant_id="tenant-1")
