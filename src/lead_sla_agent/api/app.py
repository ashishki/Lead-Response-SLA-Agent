"""FastAPI application factory and module-level ASGI app."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from lead_sla_agent.api.health import health_status
from lead_sla_agent.api.rate_limit import InMemoryRateLimiter
from lead_sla_agent.api.webhooks import InMemoryWebhookStore
from lead_sla_agent.api.webhooks import router as webhook_router
from lead_sla_agent.observability.metrics import metrics, render_prometheus_metrics
from lead_sla_agent.operator.api import router as operator_router
from lead_sla_agent.operator.knowledge_api import router as knowledge_router


def create_app() -> FastAPI:
    """Create the FastAPI app used by the service runtime."""
    app = FastAPI(title="Lead Response SLA Agent")
    app.state.webhook_store = InMemoryWebhookStore()
    app.state.rate_limiter = InMemoryRateLimiter()

    @app.get("/health", include_in_schema=False)
    async def health():
        return health_status()

    @app.get("/metrics", include_in_schema=False)
    async def prometheus_metrics():
        return PlainTextResponse(
            render_prometheus_metrics(metrics),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    app.include_router(webhook_router)
    app.include_router(operator_router)
    app.include_router(knowledge_router)
    return app


app = create_app()
