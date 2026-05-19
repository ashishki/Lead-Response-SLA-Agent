# CODEX_PROMPT.md

Version: 1.0
Date: 2026-05-19
Phase: 1

This file is the single source of truth for current implementation state. Update it before phase boundaries and before handing a task to Codex when state changes.

Execution mode: Codex-only. There is no Claude Code runtime for this project, and Codex must not invoke Codex through `codex exec` or any nested Codex CLI call.

---

## Current State

- Phase: 1
- Baseline: 0 passing tests (pre-implementation)
- Ruff: not yet configured
- Last CI: not yet configured
- Last updated: 2026-05-19
- Execution mode: Codex-only, direct task execution
- Session tokens (approx): not yet tracked
- Cumulative phase tokens (approx): not yet tracked

---

## Continuity Pointers

- Decision log: `docs/DECISION_LOG.md`
- Implementation journal: `docs/IMPLEMENTATION_JOURNAL.md`
- Evidence index: `docs/EVIDENCE_INDEX.md`
- Architecture: `docs/ARCHITECTURE.md`
- Specification: `docs/spec.md`
- Task graph: `docs/tasks.md`
- Orchestrator: `docs/prompts/ORCHESTRATOR.md` (Codex-native, no Codex CLI nesting)
- RAG reference: `docs/RAG_REFERENCE.md`
- Task-scoped context: read `Context-Refs` in `docs/tasks.md` before broad searching.

---

## Next Task

T01: Project Skeleton

Task digest:
- Create Python 3.12 package skeleton under `src/lead_sla_agent`.
- Add FastAPI app entrypoint, settings loader, dependency files, and expected module layout.
- Acceptance criteria live in `docs/tasks.md#t01-project-skeleton`.
- Applicable contract rules: no credentials in source, required env vars documented, PII-safe defaults, one logical commit.
- Execution note: implement T01 directly in the active Codex session; do not invoke Codex through `codex exec`.

---

## Fix Queue

empty

---

## Open Findings

none

---

## Completed Tasks

none

---

## Profile State: RAG

- RAG Status: ON
- Active corpora: pilot tenant approved text knowledge base
- Retrieval baseline: not yet measured
- Open retrieval findings: none
- Index schema version: rag-index-v1 planned
- Pending reindex actions: none
- Retrieval-related next tasks: T09, T10, T13, T15, T16
- Retrieval-driven tasks: none

---

## Tool-Use State

- Tool-Use Profile: ON
- Registered tool schemas: planned `tool-schema-v1` for send_message, create_or_update_lead, lookup_available_slots, book_slot, lookup_lead_history, create_human_review_task
- Unsafe-action guardrails: human gate required for unsafe message categories, explicit customer acceptance required for booking, idempotency required for write tools
- Open tool findings: none

---

## Agentic State

- Agentic Profile: ON
- Active agent roles: bounded lead qualification conversation runtime
- Loop termination contract version: planned `agent-loop-v1`
- Cross-iteration state mechanism: PostgreSQL conversation state and transcript rows
- Open agent findings: none

---

## Planning State

- Planning Profile: OFF
- Plan schema version: n/a
- Plan validation method: n/a
- Open plan findings: none

---

## Compliance State

- Compliance Status: OFF
- Active frameworks: n/a
- Controls implemented: n/a
- Controls partial: n/a
- Controls not started: n/a
- Evidence artifact: n/a
- Open compliance findings: none

---

## NFR Baseline

- API p99 latency: not yet measured
- Deterministic acknowledgement latency: not yet measured
- AI-assisted first-response p95: not yet measured
- Retrieval p95 latency: not yet measured
- Provider send failure rate: not yet measured
- Last measured: n/a
- NFR regression open: No

---

## Evaluation State

### Last Evaluation

- Profile: n/a
- Task: n/a
- Date: n/a
- Eval Source: n/a
- Metric(s): n/a
- Score: n/a
- Baseline: n/a
- Delta: n/a
- Regression: n/a

### Open Evaluation Issues

none

### Evaluation History

No evaluations have run yet.

---

## Phase History

No completed phases yet.

---

## Compaction Protocol

- Trigger when Completed Tasks exceeds 20 entries or Phase History exceeds 5 summaries.
- Preserve Current State, Next Task, Fix Queue, Open Findings, profile state blocks, and latest evaluation state.
- Move older detailed entries into an archive section only after summarizing the information needed by future agents.

---

## Instructions for Codex

1. Read `docs/IMPLEMENTATION_CONTRACT.md` before starting any task.
2. Read the full task definition in `docs/tasks.md` before writing code.
3. Read all `Depends-On` task summaries and task `Context-Refs`.
4. Do the work directly in the current Codex session; do not call `codex exec`.
5. Run `pytest` to capture the current baseline before making changes once tests exist.
6. Run `ruff check src/lead_sla_agent tests` before making changes once the project skeleton exists.
7. Write tests before or alongside implementation. Every acceptance criterion has a passing test.
8. Update active eval artifacts when a task uses a profile trigger tag.
9. Update this file at phase boundaries and when baseline, next task, open findings, or profile state changes.
10. Commit with format `type(scope): description`, one logical change per commit, and no AI co-author trailers when the user asks for a commit.
11. When done, return `IMPLEMENTATION_RESULT: DONE` with the new baseline and what changed.
12. When blocked, return `IMPLEMENTATION_RESULT: BLOCKED` with the exact blocker and the smallest unblock step.
