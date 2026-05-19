"""FastAPI application factory and module-level ASGI app."""

from __future__ import annotations

from fastapi import FastAPI

from lead_sla_agent.api.health import health_status
from lead_sla_agent.api.webhooks import InMemoryWebhookStore
from lead_sla_agent.api.webhooks import router as webhook_router
from lead_sla_agent.operator.api import router as operator_router


def create_app() -> FastAPI:
    """Create the FastAPI app used by the service runtime."""
    app = FastAPI(title="Lead Response SLA Agent")
    app.state.webhook_store = InMemoryWebhookStore()

    @app.get("/health", include_in_schema=False)
    async def health():
        return health_status()

    app.include_router(webhook_router)
    app.include_router(operator_router)
    return app


app = create_app()
