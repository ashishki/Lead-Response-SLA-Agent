"""First-response SLA timer jobs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from redis.asyncio import Redis


@dataclass
class LeadSLAState:
    lead_id: uuid.UUID
    created_at: datetime
    outbound_confirmed_at: datetime | None = None
    sla_breached_at: datetime | None = None


def record_sla_breach_if_needed(
    lead: LeadSLAState,
    now: datetime,
    response_deadline: datetime,
) -> bool:
    """Mark a lead as breached once when no outbound response exists by deadline."""
    if lead.outbound_confirmed_at is not None:
        return False
    if lead.sla_breached_at is not None:
        return False
    if now < response_deadline:
        return False

    lead.sla_breached_at = now
    return True


SLA_BREACH_SCRIPT = """
local state_key = KEYS[1]
local breach_key = KEYS[2]
local now_ms = ARGV[1]
local deadline_ms = ARGV[2]
if redis.call('HGET', state_key, 'outbound_confirmed_at') then
  return 0
end
if tonumber(now_ms) < tonumber(deadline_ms) then
  return 0
end
if not redis.call('SET', breach_key, now_ms, 'NX') then
  return 0
end
redis.call('HSET', state_key, 'sla_breached_at', now_ms)
return 1
"""


async def record_outbound_confirmed(
    client: Redis,
    tenant_id: uuid.UUID,
    lead_id: uuid.UUID,
    confirmed_at: datetime,
) -> None:
    """Persist an outbound confirmation timestamp for SLA processing."""
    await client.hset(
        _sla_state_key(tenant_id, lead_id), "outbound_confirmed_at", _millis(confirmed_at)
    )


async def record_sla_breach_once(
    client: Redis,
    tenant_id: uuid.UUID,
    lead_id: uuid.UUID,
    now: datetime,
    response_deadline: datetime,
) -> bool:
    """Atomically mark an SLA breach once when no response was confirmed."""
    result = await client.eval(
        SLA_BREACH_SCRIPT,
        2,
        _sla_state_key(tenant_id, lead_id),
        _sla_breach_key(tenant_id, lead_id),
        str(_millis(now)),
        str(_millis(response_deadline)),
    )
    return result == 1


async def get_sla_breached_at(
    client: Redis,
    tenant_id: uuid.UUID,
    lead_id: uuid.UUID,
) -> int | None:
    """Return the stored breach timestamp in milliseconds when present."""
    value = await client.hget(_sla_state_key(tenant_id, lead_id), "sla_breached_at")
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return int(value)


def _sla_state_key(tenant_id: uuid.UUID, lead_id: uuid.UUID) -> str:
    return "sla:state:" + str(tenant_id) + ":" + str(lead_id)


def _sla_breach_key(tenant_id: uuid.UUID, lead_id: uuid.UUID) -> str:
    return "sla:breached:" + str(tenant_id) + ":" + str(lead_id)


def _millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)
