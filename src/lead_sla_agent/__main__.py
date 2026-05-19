"""Command entrypoint for the Lead Response SLA Agent service."""

from __future__ import annotations

APP_IMPORT_PATH = "lead_sla_agent.api.app:app"


def main() -> None:
    """Run the ASGI application through uvicorn."""
    import uvicorn

    uvicorn.run(APP_IMPORT_PATH, factory=False)


if __name__ == "__main__":
    main()
