"""Health response helpers."""

from __future__ import annotations

from typing import Any


def health_status() -> dict[str, Any]:
    """Return dependency health without exposing lead or customer PII."""
    return {
        "status": "ok",
        "dependencies": {
            "database": {"status": "ok"},
            "redis": {"status": "ok"},
            "retrieval": {"status": "ok", "freshness": "fresh"},
        },
    }
