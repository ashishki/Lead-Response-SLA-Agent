"""CRM/spreadsheet adapter interfaces and fakes."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CRMWriteResult:
    remote_record_id: str
    status: str
    idempotency_key: str


class FakeCRMAdapter:
    def __init__(self) -> None:
        self.records_by_key: dict[str, CRMWriteResult] = {}
        self.write_count = 0

    async def create_or_update_lead(
        self,
        lead_id: uuid.UUID,
        fields: dict[str, Any],
    ) -> CRMWriteResult:
        del fields
        idempotency_key = str(lead_id)
        existing = self.records_by_key.get(idempotency_key)
        if existing is not None:
            return existing

        self.write_count += 1
        result = CRMWriteResult(
            remote_record_id=f"crm-{uuid.uuid4()}",
            status="upserted",
            idempotency_key=idempotency_key,
        )
        self.records_by_key[idempotency_key] = result
        return result
