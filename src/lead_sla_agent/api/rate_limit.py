"""Small request rate limiter for public and operator API boundaries."""

from __future__ import annotations

import hashlib
import time
from collections import deque
from dataclasses import dataclass

from fastapi import HTTPException, Request, status


@dataclass(frozen=True)
class RateLimitRule:
    scope: str
    limit: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int


DEFAULT_RATE_LIMIT_RULES = {
    "webhook": RateLimitRule(scope="webhook", limit=60, window_seconds=60),
    "operator": RateLimitRule(scope="operator", limit=120, window_seconds=60),
}


class InMemoryRateLimiter:
    """Deterministic limiter used by the app until Redis owns distributed limits."""

    def __init__(self, rules: dict[str, RateLimitRule] | None = None) -> None:
        self.rules = dict(rules or DEFAULT_RATE_LIMIT_RULES)
        self._events: dict[tuple[str, str], deque[float]] = {}

    def check(
        self,
        scope: str,
        key: str,
        now: float | None = None,
    ) -> RateLimitDecision:
        rule = self.rules[scope]
        current_time = time.monotonic() if now is None else now
        events = self._events.setdefault((scope, key), deque())
        cutoff = current_time - rule.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()

        if len(events) >= rule.limit:
            retry_after = max(1, int(rule.window_seconds - (current_time - events[0])))
            return RateLimitDecision(
                allowed=False,
                remaining=0,
                retry_after_seconds=retry_after,
            )

        events.append(current_time)
        return RateLimitDecision(
            allowed=True,
            remaining=max(0, rule.limit - len(events)),
            retry_after_seconds=0,
        )


async def enforce_webhook_rate_limit(request: Request) -> None:
    _enforce_rate_limit(request, "webhook")


async def enforce_operator_rate_limit(request: Request) -> None:
    _enforce_rate_limit(request, "operator")


def _enforce_rate_limit(request: Request, scope: str) -> None:
    limiter = _rate_limiter(request)
    decision = limiter.check(scope=scope, key=_rate_limit_key(request, scope))
    if decision.allowed:
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="rate limited",
        headers={"Retry-After": str(decision.retry_after_seconds)},
    )


def _rate_limiter(request: Request) -> InMemoryRateLimiter:
    if not hasattr(request.app.state, "rate_limiter"):
        request.app.state.rate_limiter = InMemoryRateLimiter()
    return request.app.state.rate_limiter


def _rate_limit_key(request: Request, scope: str) -> str:
    client_host = request.client.host if request.client is not None else "unknown"
    digest = hashlib.sha256(client_host.encode("utf-8")).hexdigest()[:16]
    return f"{scope}:{digest}"
