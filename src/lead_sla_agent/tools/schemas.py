"""Tool schema metadata and call contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

TOOL_SCHEMA_VERSION = "tool-schema-v1"


class SideEffectClass(StrEnum):
    READ = "read"
    WRITE = "write"
    SEND = "send"
    BOOK = "book"


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int
    backoff_seconds: float


@dataclass(frozen=True)
class ToolContract:
    name: str
    version: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    side_effect_class: SideEffectClass
    idempotency_rule: str | None
    timeout_seconds: float
    retry_policy: RetryPolicy
    human_gate_rule: str

    @property
    def requires_idempotency_key(self) -> bool:
        return self.side_effect_class != SideEffectClass.READ and self.idempotency_rule is not None


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    idempotency_key: str | None = None
