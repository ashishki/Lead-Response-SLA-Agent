# CODEX_PROMPT.md

Version: 2.0
Date: 2026-05-19
Phase: 7
Status: active

This is the compact state file for the Codex development loop. Keep it short. Do not paste completed task history here; durable history belongs in `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`, and archived task files.

Execution mode: Codex-only. Do not invoke Codex through `codex exec` or any nested Codex CLI call.

---

## Current State

- Product state: validated prototype completed through T18.
- Active task graph: `docs/tasks.md` T19-T49.
- Completed task archive: `docs/archive/tasks_T01_T18_completed.md`.
- Prior prompt archive: `docs/archive/CODEX_PROMPT_T01_T18_completed.md`.
- Last verified baseline: 58 passing tests (`.venv/bin/python -m pytest tests/ -q --tb=short`).
- Last verified lint: passing (`.venv/bin/ruff check src/lead_sla_agent tests`; `.venv/bin/ruff format --check src/lead_sla_agent tests`).
- Last phase review: `docs/audit/PHASE6_REVIEW.md`.
- Last updated: 2026-05-19.

---

## Loop Inputs

- Orchestrator: `docs/prompts/ORCHESTRATOR.md`
- Compact task prompt: `docs/prompts/LOOP_TASK_PROMPT.md`
- Active tasks: `docs/tasks.md`
- Implementation contract: `docs/IMPLEMENTATION_CONTRACT.md`
- Architecture: `docs/ARCHITECTURE.md`
- Evidence index: `docs/EVIDENCE_INDEX.md`
- Decision log: `docs/DECISION_LOG.md`
- Implementation journal: `docs/IMPLEMENTATION_JOURNAL.md`
- Eval artifacts: `docs/retrieval_eval.md`, `docs/tool_eval.md`, `docs/agent_eval.md`

---

## Next Task

T19: Database-Backed Lead, Conversation, Transcript, Review, and Outcome Repositories

Task source: `docs/tasks.md`

Task digest:
- Phase 7 starts production persistence and runtime hardening.
- Replace in-memory runtime repositories with async SQLAlchemy persistence where T19 scopes it.
- Preserve tenant isolation, PII redaction, T1 runtime, and existing eval gates.
- Do not broaden into T20 transaction/idempotency work except for interfaces required by T19 tests.

---

## Fix Queue

empty

---

## Open Findings

none

---

## Update Rules

- After each task, update only the current state, next task, fix queue, and any changed baseline lines.
- Record detailed task completion evidence in `docs/IMPLEMENTATION_JOURNAL.md`.
- Add or update canonical proof links in `docs/EVIDENCE_INDEX.md`.
- Keep this file compact; archived task history must not be copied back into this prompt.
