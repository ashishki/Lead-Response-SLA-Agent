"""Tenant context helpers for transaction-scoped database access."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

TENANT_CONTEXT_SQL = text("SELECT set_config('app.tenant_id', :tenant_id, true)")


async def apply_tenant_context(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Set transaction-local tenant context before tenant-scoped queries."""
    if tenant_id is None:
        raise ValueError("tenant_id is required")

    await session.execute(TENANT_CONTEXT_SQL, {"tenant_id": str(tenant_id)})
