"""Embedding adapter contracts for retrieval ingestion."""

from __future__ import annotations

import hashlib
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Protocol

from lead_sla_agent.config import Settings

EMBEDDING_MODEL = "local-hash-embedding-v1"
PRODUCTION_EMBEDDING_MODEL = "text-embedding-3-small"
PRODUCTION_EMBEDDING_DIMENSIONS = 1536


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


class EmbeddingHTTPResponse(Protocol):
    status_code: int

    def json(self) -> dict[str, Any]:
        """Return a decoded embedding provider response body."""


class EmbeddingHTTPClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> Awaitable[EmbeddingHTTPResponse]:
        """Request embeddings from a provider."""


class OpenAIEmbeddingClient:
    """OpenAI embedding adapter with injectable HTTP transport for tests."""

    def __init__(
        self,
        api_key: str,
        http_client: EmbeddingHTTPClient,
        model_name: str = PRODUCTION_EMBEDDING_MODEL,
        dimensions: int = PRODUCTION_EMBEDDING_DIMENSIONS,
        api_url: str = "https://api.openai.com/v1/embeddings",
        timeout_seconds: float = 20,
    ) -> None:
        self.api_key = api_key
        self.http_client = http_client
        self.model_name = model_name
        self.dimensions = dimensions
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        http_client: EmbeddingHTTPClient,
    ) -> OpenAIEmbeddingClient:
        """Build the adapter from embedding-specific settings only."""
        return cls(
            api_key=settings.embedding_api_key,
            model_name=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            api_url=settings.embedding_api_url,
            http_client=http_client,
        )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = await self.http_client.post(
                self.api_url,
                headers={
                    "authorization": "Bearer " + self.api_key,
                    "content-type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "input": texts,
                    "dimensions": self.dimensions,
                    "encoding_format": "float",
                },
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            raise EmbeddingServiceError("embedding provider timeout") from exc

        if response.status_code >= 400:
            raise EmbeddingServiceError("embedding provider request failed")

        body = response.json()
        vectors_by_index = {
            int(item["index"]): [float(value) for value in item["embedding"]]
            for item in body.get("data", [])
        }
        vectors = [vectors_by_index[index] for index in range(len(texts))]
        if any(len(vector) != self.dimensions for vector in vectors):
            raise EmbeddingServiceError("embedding provider returned unexpected dimensions")
        return vectors
