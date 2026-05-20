# ADR-002: Production Embedding Provider

Status: Accepted
Date: 2026-05-20

## Context

The retrieval baseline currently uses `local-hash-embedding-v1`, an 8-dimensional deterministic adapter for tests. Phase 9 requires a production text embedding provider for pilot corpora while preserving deterministic fake embeddings in normal tests.

Official OpenAI documentation for embeddings lists `text-embedding-3-small` as a current third-generation embedding model. The embeddings guide states that the default vector length is 1536 for `text-embedding-3-small` and 3072 for `text-embedding-3-large`, and that the embeddings endpoint supports a `dimensions` parameter for `text-embedding-3` models.

Sources:

- https://platform.openai.com/docs/guides/embeddings
- https://platform.openai.com/docs/models/text-embedding-3-small

## Decision

Use OpenAI `text-embedding-3-small` as the production embedding model for v1.

Configuration:

- Model: `text-embedding-3-small`
- Dimensions: `1536`
- Index schema version: `rag-index-v1`
- Retrieval mode: text-only
- API URL: `https://api.openai.com/v1/embeddings`

## Consequences

Changing the embedding model, dimensions, or metadata schema requires:

1. A new ADR.
2. A full reindex plan for every active tenant corpus.
3. An update to `docs/retrieval_eval.md`.
4. A comparison against the deterministic retrieval baseline and the prior production embedding baseline.

Normal CI tests must use deterministic or fake-provider embeddings. Live OpenAI embedding checks are opt-in only and must require explicit credentials outside the default test suite.
