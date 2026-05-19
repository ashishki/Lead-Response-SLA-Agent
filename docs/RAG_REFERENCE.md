# RAG Reference - Dream Motif Interpreter

Version: 1.0
Last updated: 2026-05-19
Source: https://github.com/ashishki/Dream_Motif_Interpreter

This file is a scoped reference for the Lead Response SLA Agent RAG work. It is not a dependency and must not be copied blindly. The source project is a single-user dream archive; this project is a tenant-scoped lead-response system with customer PII and external side effects. Adapt patterns, not domain assumptions.

---

## Relevant Source Areas

| Area | Reference path in Dream Motif Interpreter | Why it matters here |
|------|-------------------------------------------|---------------------|
| Source contracts | `app/retrieval/types.py` | Defines `SourceConnector`, `FetchedSourceDocument`, `NormalizedDocument`, and shared `EmbeddingClient` style boundaries. |
| Ingestion pipeline | `app/retrieval/ingestion.py` | Shows connector -> normalized document -> parser/validation -> chunk -> embed -> upsert flow, including content hashes and duplicate skip behavior. |
| Query pipeline | `app/retrieval/query.py` | Shows separate query-time retrieval, typed evidence blocks, typed insufficient-evidence result, hybrid vector + FTS retrieval, and exact-search fallback. |
| pgvector index | `alembic/versions/006_add_hnsw_index.py` | Shows pgvector HNSW index creation for cosine search. Adapt with tenant/customer filters and migration safety. |
| Retrieval eval | `docs/retrieval_eval.md` and `scripts/eval.py` | Shows retrieval metrics, eval source requirement, answer-quality separation, real regression datasets, and no-answer checks. |
| Tests | `tests/integration/test_rag_ingestion.py`, `tests/integration/test_rag_query.py`, `tests/integration/test_retrieval_eval.py` | Useful reference shape for ingestion/query/eval tests. |

---

## Patterns To Reuse

- Keep ingestion and query-time retrieval in separate modules.
- Define source connector contracts before provider-specific integrations.
- Normalize provider payloads into a project-owned `NormalizedDocument` before parsing or chunking.
- Store source document ID, source path/title, content hash, chunk ordinal, index schema version, and freshness metadata.
- Make ingestion idempotent by source identity plus content hash; unchanged sources should not re-embed.
- Handle duplicate source candidates fail-soft with non-PII warnings instead of aborting an entire sync.
- Put embedding calls behind a shared `EmbeddingClient` protocol/adapter with typed HTTP errors and tracing.
- Use token-aware chunking with explicit max tokens and overlap once a tokenizer/model is selected.
- Use PostgreSQL pgvector for v1 and add an HNSW index when corpus size or latency requires it.
- Consider hybrid retrieval: vector candidates plus PostgreSQL FTS candidates fused by reciprocal rank fusion.
- Add exact keyword/FTS recall for concrete lookup cases where vector thresholding may suppress obvious evidence.
- Return a typed `insufficient_evidence` result with a reason; do not let retrieval code draft answers.
- Track retrieval quality separately from answer quality.
- Require every eval entry to include an exact eval source and date.
- Require corpus version, root-cause classification, and separation of retrieval quality from answer quality for every metrics-changing run.

---

## Required Adaptations For This Project

- Add tenant/customer corpus isolation to every ingestion and query path. Dream Motif Interpreter is single-user; Lead Response SLA Agent is not.
- Treat lead text, customer contact details, transcripts, and provider IDs as PII. Do not log raw query text, raw customer messages, or provider identifiers.
- Use approved business knowledge only. Do not use external web search for customer-facing business answers in v1.
- Prefer text-only retrieval for v1. Multimodal retrieval remains out of scope.
- Keep customer-facing reply drafting outside retrieval. Retrieval returns evidence or `insufficient_evidence`; conversation policy decides handoff or drafting.
- Exact keyword recall should support business entities and policy terms such as service names, service areas, product/package names, cancellation terms, and price labels.
- Evaluation datasets must include unsupported regulated-advice queries, stale/unknown policy questions, and tenant-isolation checks.

---

## Implementation Notes For T09/T10

T09 should define source and normalized document types before provider-specific ingestion. A good local shape is:

- `SourceDocumentRef`
- `FetchedSourceDocument`
- `NormalizedDocument`
- `KnowledgeChunkDraft`
- `EmbeddingClient`
- `EmbeddingServiceError`

T10 should define query result types before retrieval implementation. A good local shape is:

- `EvidenceBlock`
- `EvidenceSnippet`
- `InsufficientEvidence`
- `RetrievalResult`

Do not copy Dream Motif Interpreter names that are domain-specific to dreams. Use lead/business knowledge names.

---

## Evaluation Implications

`docs/retrieval_eval.md` should eventually include:

- hit@3
- hit@5
- MRR
- citation precision
- no-answer accuracy
- retrieval p95 latency
- answer faithfulness/completeness/relevance when reply drafting exists
- eval source and date for every run
- corpus version for every run
- explicit notes separating corpus-change-induced and code-change-induced metric changes
