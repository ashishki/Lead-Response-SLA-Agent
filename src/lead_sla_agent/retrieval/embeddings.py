"""Embedding adapter contracts for retrieval ingestion."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

EMBEDDING_MODEL = "local-hash-embedding-v1"


class EmbeddingServiceError(RuntimeError):
    """Raised when an embedding adapter cannot produce vectors."""


class EmbeddingClient(Protocol):
    model_name: str

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text chunks."""


@dataclass
class DeterministicHashEmbeddingClient:
    """Deterministic local embedding adapter for tests and baseline metadata."""

    model_name: str = EMBEDDING_MODEL
    dimensions: int = 8

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255 for byte in digest[: self.dimensions]]
