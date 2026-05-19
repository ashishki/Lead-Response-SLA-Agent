"""Shared tracing entrypoint."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.trace import Tracer


def get_tracer(name: str = "lead_sla_agent") -> Tracer:
    """Return an OpenTelemetry tracer for application code."""
    return trace.get_tracer(name)
