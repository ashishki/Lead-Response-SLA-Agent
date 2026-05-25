# CODEX_PROMPT.md

Version: 2.0
Date: 2026-05-21
Phase: 20
Status: active

This is the compact state file for the Codex development loop. Keep it short. Do not paste completed task history here; durable history belongs in `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`, and archived task files.

Execution mode: Codex-only. Do not invoke Codex through `codex exec` or any nested Codex CLI call.

---

## Current State

- Product state: validated prototype completed through T18; first production-readiness task graph completed through T49; production hardening backlog completed through T66 and defined through T69; solo public vertical showcase Phase 22 completed through T77; pre-pilot evidence package completed through T67a.
- Active task graph: blocked real-data T67-T69. Phase 22 T70-T77 complete.
- Completed task archive: `docs/archive/tasks_T01_T18_completed.md`.
- Prior prompt archive: `docs/archive/CODEX_PROMPT_T01_T18_completed.md`.
- Last verified baseline: 265 passed, 26 skipped (`DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` against isolated local PostgreSQL and Redis).
- Last verified lint: passing (`.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py`; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py`).
- Last phase review: `docs/audit/PHASE20_REVIEW.md`.
- Last updated: 2026-05-25.

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

T67: Real-Data Eval and Operator Feedback Loop

Task source: `docs/tasks.md`

Task digest:
- Convert de-identified pilot transcripts and operator corrections into retrieval, tool, and agent regression evals.
- Requires approved real pilot feedback/export data before implementation.
- Stop until a human supplies or approves real pilot artifacts for de-identification.

---

## Fix Queue

- If Phase 22 lacks data, follow `docs/market/open_source_research_protocol.md` and gather public sources with citations instead of stopping.
- T67 is blocked pending approved real pilot transcripts, operator corrections, provider failure/retry cases, and human approval metadata for eval use.
- T67a may proceed only as pre-pilot controlled evidence; do not rename it or treat it as real-data eval proof.

---

## Open Findings

none

---

## Update Rules

- After each task, update only the current state, next task, fix queue, and any changed baseline lines.
- Record detailed task completion evidence in `docs/IMPLEMENTATION_JOURNAL.md`.
- Add or update canonical proof links in `docs/EVIDENCE_INDEX.md`.
- Keep this file compact; archived task history must not be copied back into this prompt.
