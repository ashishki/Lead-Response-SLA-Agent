"""Lead-history lookup adapter."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class LeadHistoryResult:
    tenant_id: uuid.UUID
    lead_id: uuid.UUID
    events: list[str]


class FakeLeadHistoryAdapter:
    def __init__(self) -> None:
        self.history: dict[tuple[uuid.UUID, uuid.UUID], list[str]] = {}

    async def lookup_lead_history(
        self,
        tenant_id: uuid.UUID,
        lead_id: uuid.UUID,
    ) -> LeadHistoryResult:
        return LeadHistoryResult(
            tenant_id=tenant_id,
            lead_id=lead_id,
            events=self.history.get((tenant_id, lead_id), []),
        )
