# Retrieval Evaluation - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Profile: RAG ON
Retrieval mode: text-only

---

## Purpose

This artifact tracks retrieval quality separately from code quality. RAG tasks are not complete until this file records current results, baseline comparison, and any regression notes.

---

## Architecture Metadata

| Field | Value |
|-------|-------|
| Index schema version | `rag-index-v1` planned |
| Retrieval mode | text-only |
| Embedding model | pending T09 implementation decision |
| Chunking strategy | section/heading-aware chunks planned |
| Max index age | 24 hours |
| Corpus scope | Tenant-approved FAQs, pricing ranges, service descriptions, service-area rules, cancellation policies, booking rules, escalation instructions |
| Unsupported-answer behavior | Return `insufficient_evidence` and create human-review task |

---

## Evaluation Dataset

Seed dataset path: `tests/eval/fixtures/retrieval_seed.json`

Initial dataset requirements:
- At least 10 queries.
- Include pricing, service area, booking, cancellation, supported FAQ, unsupported legal/medical/financial, and stale/unknown policy scenarios.
- Each query includes expected source document IDs or expected `insufficient_evidence`.

---

## Metrics

| Metric | Target | Regression rule |
|--------|--------|-----------------|
| hit@3 | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| citation precision | Baseline established in T10 | Any drop below accepted baseline is P1 unless justified and approved |
| no-answer accuracy | Baseline established in T10 | Any false answer for unsupported query is P1 |
| retrieval p95 latency | Target recorded in `docs/nfr.md` | More than 10 percent over baseline is P2; safety regression is P1 |

---

## Evaluation History

| Date | Task | Corpus version | Dataset | Metrics | Result | Notes |
|------|------|----------------|---------|---------|--------|-------|
| 2026-05-19 | Bootstrap | n/a | planned seed dataset | not yet measured | pending | Baseline will be established by T09/T10. |

---

## Open Retrieval Findings

none

---

## Regression Notes

none
