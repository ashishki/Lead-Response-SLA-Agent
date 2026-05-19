from __future__ import annotations

import ast
from pathlib import Path

QUEUE_MODULES = [
    Path("src/lead_sla_agent/workers/queue.py"),
    Path("src/lead_sla_agent/workers/sla.py"),
    Path("src/lead_sla_agent/workers/retries.py"),
]


def test_only_async_redis_imported() -> None:
    imported_modules: list[str] = []
    for path in QUEUE_MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.append(node.module)

    assert "redis.asyncio" in imported_modules
    assert "redis" not in imported_modules
