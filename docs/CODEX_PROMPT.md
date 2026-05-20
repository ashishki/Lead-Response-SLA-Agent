# CODEX_PROMPT.md

Version: 2.0
Date: 2026-05-20
Phase: 17
Status: active

This is the compact state file for the Codex development loop. Keep it short. Do not paste completed task history here; durable history belongs in `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`, and archived task files.

Execution mode: Codex-only. Do not invoke Codex through `codex exec` or any nested Codex CLI call.

---

## Current State

- Product state: validated prototype completed through T18; first production-readiness task graph completed through T49; production hardening backlog completed through T56 and defined through T69.
- Active task graph: `docs/tasks.md` T50-T69.
- Completed task archive: `docs/archive/tasks_T01_T18_completed.md`.
- Prior prompt archive: `docs/archive/CODEX_PROMPT_T01_T18_completed.md`.
- Last verified baseline: 215 passing tests (`DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` against isolated local PostgreSQL and Redis).
- Last verified lint: passing (`.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py`; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py`).
- Last phase review: `docs/audit/PHASE17_REVIEW.md`.
- Last updated: 2026-05-20.

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

T57: Live Messaging Provider Pilot Path

Task source: `docs/tasks.md`

Task digest:
- Configure the first live messaging provider for one pilot tenant with human approval enforced before every outbound message.
- Live provider credentials must be environment-scoped and never required for normal tests.
- Provider send path must record provider message ID, latency, delivery status, failure reason, rate-limit/failure handling, and operator-visible fallback behavior.
- Preserve T1 runtime, tenant isolation, PII redaction, existing eval gates, and human approval boundaries.

---

## Fix Queue

- T57 is blocked pending human selection/approval of the first live messaging provider for the pilot (for example Postmark, SendGrid, SMTP, or another provider) and confirmation that using the existing generic email adapter contract is acceptable until real credentials are configured.

---

## Open Findings

none

---

## Update Rules

- After each task, update only the current state, next task, fix queue, and any changed baseline lines.
- Record detailed task completion evidence in `docs/IMPLEMENTATION_JOURNAL.md`.
- Add or update canonical proof links in `docs/EVIDENCE_INDEX.md`.
- Keep this file compact; archived task history must not be copied back into this prompt.
