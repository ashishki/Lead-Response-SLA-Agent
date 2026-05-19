"""Small metrics facade used until a backend exporter is configured."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class InMemoryMetrics:
    """In-process metrics collector for deterministic unit tests."""

    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    histograms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def observe(self, name: str, value: float) -> None:
        self.histograms[name].append(value)

    def reset(self) -> None:
        self.counters.clear()
        self.histograms.clear()


metrics = InMemoryMetrics()
