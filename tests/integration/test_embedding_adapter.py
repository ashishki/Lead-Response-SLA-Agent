from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from lead_sla_agent.config import Settings
from lead_sla_agent.retrieval.embeddings import (
    PRODUCTION_EMBEDDING_DIMENSIONS,
    PRODUCTION_EMBEDDING_MODEL,
    DeterministicHashEmbeddingClient,
    EmbeddingServiceError,
    OpenAIEmbeddingClient,
)


@dataclass(frozen=True)
class FakeEmbeddingResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class FakeEmbeddingHTTPClient:
    def __init__(self, response: FakeEmbeddingResponse) -> None:
        self.response = response
        self.requests: list[dict[str, Any]] = []

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> FakeEmbeddingResponse:
        self.requests.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return self.response


def _embedding_response(count: int, dimensions: int) -> FakeEmbeddingResponse:
    return FakeEmbeddingResponse(
        200,
        {
            "data": [
                {"index": index, "embedding": [float(index + 1)] * dimensions}
                for index in range(count)
            ]
        },
    )


@pytest.mark.asyncio
async def test_openai_embedding_adapter_uses_fake_provider_and_records_dimensions() -> None:
    http_client = FakeEmbeddingHTTPClient(_embedding_response(2, PRODUCTION_EMBEDDING_DIMENSIONS))
    adapter = OpenAIEmbeddingClient.from_settings(
        Settings(
            EMBEDDING_API_KEY="test-embedding-key",
            EMBEDDING_MODEL=PRODUCTION_EMBEDDING_MODEL,
            EMBEDDING_DIMENSIONS=PRODUCTION_EMBEDDING_DIMENSIONS,
        ),
        http_client,
    )

    vectors = await adapter.embed_texts(["service area", "booking policy"])

    assert adapter.model_name == PRODUCTION_EMBEDDING_MODEL
    assert adapter.dimensions == PRODUCTION_EMBEDDING_DIMENSIONS
    assert len(vectors) == 2
    assert all(len(vector) == PRODUCTION_EMBEDDING_DIMENSIONS for vector in vectors)
    assert http_client.requests[0]["headers"]["authorization"] == "Bearer test-embedding-key"
    assert http_client.requests[0]["json"] == {
        "model": PRODUCTION_EMBEDDING_MODEL,
        "input": ["service area", "booking policy"],
        "dimensions": PRODUCTION_EMBEDDING_DIMENSIONS,
        "encoding_format": "float",
    }


@pytest.mark.asyncio
async def test_openai_embedding_adapter_rejects_unexpected_dimensions() -> None:
    adapter = OpenAIEmbeddingClient(
        api_key="test-embedding-key",
        http_client=FakeEmbeddingHTTPClient(_embedding_response(1, 3)),
        dimensions=PRODUCTION_EMBEDDING_DIMENSIONS,
    )

    with pytest.raises(EmbeddingServiceError, match="unexpected dimensions"):
        await adapter.embed_texts(["service area"])


@pytest.mark.asyncio
async def test_deterministic_embedding_baseline_remains_available() -> None:
    adapter = DeterministicHashEmbeddingClient()

    vectors = await adapter.embed_texts(["service area"])

    assert adapter.model_name == "local-hash-embedding-v1"
    assert adapter.dimensions == 8
    assert len(vectors[0]) == 8
