"""First-response SLA timer jobs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


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
