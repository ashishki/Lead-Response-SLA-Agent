"""Lead outcome label storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class OutcomeStore:
    labels: list[dict[str, Any]] = field(default_factory=list)

    async def add_label(
        self,
        tenant_id: str,
        lead_id: str,
        label: str,
        labeled_on: date,
    ) -> dict[str, Any]:
        row = {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "label": label,
            "labeled_on": labeled_on.isoformat(),
        }
        self.labels.append(row)
        return row

    async def query_labels(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        return [
            row
            for row in self.labels
            if row["tenant_id"] == tenant_id
            and start_date <= date.fromisoformat(row["labeled_on"]) <= end_date
        ]
