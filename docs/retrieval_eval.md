# Retrieval Evaluation - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Profile: RAG ON
Retrieval mode: text-only

---

## Purpose

This artifact tracks retrieval quality separately from code quality. RAG tasks are not complete until this file records current results, baseline comparison, and any regression notes.

---

## Evaluation Validity Rule

An evaluation entry is invalid and must be rejected if any of the following is true:

- `Eval Source` is absent, blank, or too vague.
- `Date` is absent or blank.
- `Corpus version` is absent or blank.
- Metrics are recorded without the dataset or scenario slice used to produce them.

Acceptable `Eval Source` examples:

- `python -m pytest tests/eval/test_retrieval_eval.py::test_seed_hit_at_3, run 2026-05-19`
- `scripts/eval_retrieval.py against tests/eval/fixtures/retrieval_seed.json, run 2026-05-19`
- `manual spot-check: Q01-Q05 retrieved evidence inspected against source docs, run 2026-05-19`

Invalid examples:

- `Ran evaluation`
- `Updated metrics`
- `Tests passed`
- `Manual check`

An invalid entry counts as a missing evaluation. A RAG task with a missing evaluation is not complete.

---

## Retrieval Quality vs Answer Quality

Retrieval quality and answer quality are separate gates.

- Retrieval quality measures whether the system surfaced the right evidence.
- Answer quality measures whether the reply used that evidence faithfully.

A fluent answer can hide bad retrieval. Correct retrieval can still lead to a bad answer. A passing answer-quality check does not close a retrieval regression, and green unit tests do not prove retrieval quality.

---

## Architecture Metadata

| Field | Value |
|-------|-------|
| Index schema version | `rag-index-v1` |
| Retrieval mode | text-only |
| Reference implementation | `docs/RAG_REFERENCE.md`, based on `https://github.com/ashishki/Dream_Motif_Interpreter` |
| Embedding model | `local-hash-embedding-v1` |
| Chunking strategy | markdown-heading-v1 |
| Baseline status | T10 seed retrieval baseline established |
| Max index age | 24 hours |
| Corpus scope | Tenant-approved FAQs, pricing ranges, service descriptions, service-area rules, cancellation policies, booking rules, escalation instructions |
| Unsupported-answer behavior | Return `insufficient_evidence` and create human-review task |
| Candidate retrieval | pgvector baseline; evaluate PostgreSQL FTS / reciprocal rank fusion and exact recall for concrete business terms |

---

## Evaluation Dataset

Seed dataset path: `tests/eval/fixtures/retrieval_seed.json`

Initial dataset requirements:
- At least 10 queries.
- Include pricing, service area, booking, cancellation, supported FAQ, exact business-term lookup, unsupported legal/medical/financial, stale/unknown policy, and tenant-isolation scenarios.
- Each query includes expected source document IDs or expected `insufficient_evidence`.
- Each query records whether it belongs to baseline, no-answer, exact-recall, tenant-isolation, stale-policy, or pilot-regression slice.

## Required Seed Slices

| Slice | Minimum cases | Purpose |
|-------|---------------|---------|
| Supported policy / FAQ | 3 | Verify common grounded answers retrieve the correct approved documents. |
| Exact business-term recall | 2 | Verify concrete service names, package names, locations, price labels, or policy terms are found even when vector ranking is weak. |
| Unsupported / regulated advice | 2 | Verify unrelated or regulated questions return `insufficient_evidence`. |
| Stale / unknown policy | 1 | Verify outdated or absent policy cannot produce a customer-facing answer. |
| Tenant isolation | 2 | Verify tenant A queries cannot retrieve tenant B documents. |

---

## Metrics

| Metric | Target | Regression rule |
|--------|--------|-----------------|
| hit@3 | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| hit@5 | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| MRR | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| citation precision | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| no-answer accuracy | Baseline established in T10 | Any false answer for unsupported query is P1 |
| retrieval p95 latency | Target recorded in `docs/nfr.md` | More than 10 percent over baseline is P2; safety regression is P1 |

## Regression Policy

Every metric change must be classified as one of:

- `code-change-induced`: retrieval code, query logic, embedding model, chunking, ranking, filtering, evidence assembly, or insufficient-evidence behavior changed.
- `corpus-change-induced`: approved documents changed, documents were added/removed, or a re-index changed corpus contents without retrieval code changing.
- `eval-change-induced`: dataset, expected document IDs, or metric calculation changed.

Regression rules:

- Any false customer-facing answer for an unsupported/no-answer query is P1.
- Any cross-tenant evidence leak is P1.
- Any drop in no-answer accuracy is P1 unless the human explicitly accepts the new behavior before phase gate.
- Any drop in hit@3, hit@5, MRR, or citation precision is P1 unless documented with root-cause classification, tradeoff justification, and human approval.
- Retrieval p95 latency more than 10 percent worse than baseline is P2 unless it affects first-response SLA, in which case it is P1.
- Green tests do not close retrieval regressions unless the eval history row names the exact eval source and result.

## Answer Quality Metrics

Answer quality is evaluated separately from retrieval quality once customer-facing reply drafting exists. Required dimensions:

- faithfulness: answer contains only claims supported by retrieved evidence
- completeness: answer addresses the customer question within the evidence boundary
- relevance: answer stays on the lead-response task and policy topic

Do not use answer quality to mask retrieval regressions.

---

## Evaluation History

| Date | Task | Eval Source | Corpus version | Dataset | Metrics | Root cause | Result | Notes |
|------|------|-------------|----------------|---------|---------|------------|--------|-------|
| 2026-05-19 | Bootstrap | documentation initialization; no retrieval run yet | n/a | planned seed dataset | not yet measured | n/a | pending | Baseline will be established by T09/T10. |
| 2026-05-19 | T09 | `.venv/bin/python -m pytest tests/eval/test_retrieval_eval.py::test_retrieval_eval_metadata_initialized tests/integration/test_retrieval_ingestion.py, run 2026-05-19` | `rag-index-v1` | `tests/eval/fixtures/retrieval_seed.json` planned seed path | ingestion metadata only; retrieval quality not yet measured | code-change-induced | pass | Text-only ingestion metadata initialized with deterministic local embedding adapter; retrieval metric baseline remains pending T10. |
| 2026-05-19 | T10 | `.venv/bin/python -m pytest tests/eval/test_retrieval_eval.py::test_retrieval_eval_computes_seed_metrics tests/integration/test_retrieval_query.py, run 2026-05-19` | `rag-index-v1` | `tests/eval/fixtures/retrieval_seed.json` | hit@3=1.00; hit@5=1.00; MRR=1.00; citation_precision=1.00; no-answer accuracy=1.00; retrieval_p95_latency_ms<1 local | code-change-induced | pass | Tenant filtering and insufficient-evidence handoff covered by integration tests; local deterministic baseline only. |

---

## Open Retrieval Findings

none

---

## Regression Notes

none
