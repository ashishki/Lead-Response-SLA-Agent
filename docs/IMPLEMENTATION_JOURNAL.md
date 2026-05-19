# Implementation Journal - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Status: append-only

This file records durable handoff context across agents and sessions. It is not the source of truth for architecture or policy.

---

## Journal Entry Template

```markdown
### YYYY-MM-DD - TNN - Short Title

- Scope: files, directories, or task IDs
- Why this work happened: reason or trigger
- Decisions applied: decision log or ADR refs, or "none"
- Evidence collected: tests, evals, review reports, or manual checks
- Follow-ups: next task, open risk, or "none"
- Notes for next agent: only context worth carrying forward
```

---

## Entries

### 2026-05-19 - Phase 6 Review - Evaluation and Deployment Readiness

- Scope: T16-T18, `docs/audit/PHASE6_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 6 tasks completed and the orchestrator requires a phase-boundary verification artifact.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 58 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed; `docker-compose -f compose.yml config` -> passed
- Follow-ups: task graph complete; independent review should be a fresh Codex session or human review if desired.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T18 - Deployment and Operator Runbook

- Scope: `Dockerfile`, `compose.yml`, `docs/runbook.md`, `tests/unit/test_deployment_docs.py`
- Why this work happened: T18 required T1 deployment files, environment documentation, seed-data instructions, backup/rollback notes, and an operator runbook.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_deployment_docs.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 58 passed; `docker-compose -f compose.yml config` -> passed; ruff lint/format passed
- Follow-ups: complete Phase 6 review
- Notes for next agent: Docker Compose v2 plugin syntax was not available locally; legacy `docker-compose` validated the file.

### 2026-05-19 - T17 - Metrics, Health, and NFR Baseline

- Scope: `src/lead_sla_agent/observability/metrics.py`, `src/lead_sla_agent/api/health.py`, `src/lead_sla_agent/workers/outbound.py`, `tests/integration/test_metrics.py`, `tests/integration/test_health.py`, `tests/unit/test_nfr_doc.py`, `docs/nfr.md`
- Why this work happened: T17 required workflow metrics, dependency health status without PII, and pilot NFR target initialization.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_metrics.py tests/integration/test_health.py tests/unit/test_nfr_doc.py -q --tb=short` -> 4 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 55 passed; ruff lint/format passed
- Follow-ups: continue to T18
- Notes for next agent: health reports database, Redis, and retrieval freshness status without lead/customer PII.

### 2026-05-19 - T16 - Active Profile Eval Gates in CI

- Scope: `.github/workflows/ci.yml`, `tests/unit/test_ci_eval_gates.py`, `tests/eval/test_eval_artifacts.py`, `src/lead_sla_agent/retrieval/eval.py`, `docs/EVIDENCE_INDEX.md`
- Why this work happened: T16 required active RAG, Tool-Use, and Agentic evals in CI plus regression checks.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_ci_eval_gates.py tests/eval/test_eval_artifacts.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 52 passed; ruff lint/format passed
- Follow-ups: continue to T17
- Notes for next agent: simulated no-answer regression raises an assertion through `assert_no_answer_baseline`.

### 2026-05-19 - Phase 5 Review - Conversation Runtime and Human Review

- Scope: T13-T15, `docs/audit/PHASE5_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 5 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 49 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T16 Active Profile Eval Gates in CI
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T15 - End-to-End Lead Workflow

- Scope: `src/lead_sla_agent/workers/outbound.py`, `tests/integration/test_end_to_end_workflow.py`
- Why this work happened: T15 required connecting intake, lead creation, retrieval, conversation runtime, outbound send, and operator escalation in one workflow path.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_end_to_end_workflow.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 49 passed; ruff lint/format passed
- Follow-ups: complete Phase 5 review, then continue to T16
- Notes for next agent: workflow records first-response latency and termination reason for each processed inbound event.

### 2026-05-19 - T14 - Human Review Queue and Operator Actions

- Scope: `src/lead_sla_agent/operator/`, `tests/integration/test_operator_review.py`
- Why this work happened: T14 required authenticated operator APIs for review listing, approval audit fields, and outcome label querying.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_operator_review.py -q --tb=short` -> 4 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 46 passed; ruff lint/format passed
- Follow-ups: continue to T15
- Notes for next agent: bearer token auth is a test placeholder; routes reject unauthenticated access before data reads.

### 2026-05-19 - T13 - Bounded Conversation Loop

- Scope: `src/lead_sla_agent/conversation/`, `tests/integration/test_conversation_loop.py`, `tests/eval/test_agent_eval.py`, `docs/agent_eval.md`
- Why this work happened: T13 required the bounded conversation runtime, explicit termination reasons, and agent eval baseline metadata.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_conversation_loop.py tests/eval/test_agent_eval.py -q --tb=short` -> 4 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 42 passed; ruff lint/format passed
- Follow-ups: continue to T14
- Notes for next agent: runtime is deterministic and bounded; no model calls, shell access, hidden memory, or runtime subagents.

### 2026-05-19 - Phase 4 Review - Tool Schemas and Integrations

- Scope: T11-T12, `docs/audit/PHASE4_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 4 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 38 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T13 Bounded Conversation Loop
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T12 - Provider Adapters

- Scope: `src/lead_sla_agent/tools/messaging.py`, `src/lead_sla_agent/tools/calendar.py`, `src/lead_sla_agent/tools/crm.py`, `src/lead_sla_agent/tools/lead_history.py`, `src/lead_sla_agent/operator/review_queue.py`, `tests/integration/test_provider_adapters.py`, `tests/eval/test_tool_eval.py`, `docs/tool_eval.md`
- Why this work happened: T12 required provider adapter interfaces and test doubles without hardcoded credentials.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_provider_adapters.py tests/eval/test_tool_eval.py -q --tb=short` -> 5 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 38 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Follow-ups: complete Phase 4 review, then continue to T13
- Notes for next agent: fake providers require no live credentials; CRM adapter returns the existing mapping for duplicate lead-ID writes.

### 2026-05-19 - T11 - Tool Catalog and Unsafe-Action Gates

- Scope: `src/lead_sla_agent/tools/catalog.py`, `src/lead_sla_agent/tools/schemas.py`, `src/lead_sla_agent/tools/safety.py`, `src/lead_sla_agent/tools/executor.py`, `tests/unit/test_tool_catalog.py`, `tests/unit/test_tool_safety.py`, `tests/eval/test_tool_eval.py`, `docs/tool_eval.md`
- Why this work happened: T11 required versioned tool metadata, idempotency enforcement, unsafe-action human-review routing, and tool eval metadata.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_tool_catalog.py tests/unit/test_tool_safety.py tests/eval/test_tool_eval.py -q --tb=short` -> 4 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 34 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Follow-ups: continue to T12 Provider Adapters
- Notes for next agent: `execute_tool_call` rejects side-effecting calls without an idempotency key before provider execution.

### 2026-05-19 - Phase 3 Review - Retrieval and Knowledge Grounding

- Scope: T09-T10, `docs/audit/PHASE3_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 3 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: `D-009`
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 30 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T11 Tool Catalog and Unsafe-Action Gates
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T10 - Query-Time Retrieval and Insufficient Evidence

- Scope: `src/lead_sla_agent/retrieval/query.py`, `src/lead_sla_agent/retrieval/evidence.py`, `src/lead_sla_agent/retrieval/eval.py`, `tests/integration/test_retrieval_query.py`, `tests/eval/test_retrieval_eval.py`, `tests/eval/fixtures/retrieval_seed.json`, `docs/retrieval_eval.md`
- Why this work happened: T10 required tenant-scoped retrieval, insufficient-evidence handoff without answer text, and a retrieval seed metrics baseline.
- Decisions applied: `D-009`
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_retrieval_query.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 4 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 30 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: complete Phase 3 review, then continue to T11
- Notes for next agent: retrieval code returns evidence or `insufficient_evidence`; it does not draft customer-facing answers.

### 2026-05-19 - T09 - Knowledge Ingestion Pipeline

- Scope: `src/lead_sla_agent/retrieval/documents.py`, `src/lead_sla_agent/retrieval/chunking.py`, `src/lead_sla_agent/retrieval/embeddings.py`, `src/lead_sla_agent/retrieval/ingestion.py`, `tests/integration/test_retrieval_ingestion.py`, `tests/eval/test_retrieval_eval.py`, `docs/retrieval_eval.md`, `docs/DECISION_LOG.md`
- Why this work happened: T09 required text-only RAG ingestion with source contracts, heading-aware chunks, deterministic embedding adapter, idempotent chunk upsert, and initialized retrieval eval metadata.
- Decisions applied: `D-009`
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_retrieval_ingestion.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 27 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T10 Query-Time Retrieval and Insufficient Evidence
- Notes for next agent: retrieval eval metadata is initialized, but retrieval quality metrics are intentionally pending T10.

### 2026-05-19 - Phase 2 Review - Intake and Lead State

- Scope: T06-T08, `docs/audit/PHASE2_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 2 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 24 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T09 Knowledge Ingestion Pipeline
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T08 - SLA Timers and Retry Queue

- Scope: `src/lead_sla_agent/workers/queue.py`, `src/lead_sla_agent/workers/sla.py`, `src/lead_sla_agent/workers/retries.py`, `tests/integration/test_sla_queue.py`, `tests/unit/test_async_redis.py`
- Why this work happened: T08 required async Redis queue helpers, idempotent first-response SLA breach marking, and retry exhaustion fallback to human review.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_sla_queue.py tests/unit/test_async_redis.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 24 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: complete Phase 2 review, then continue to T09
- Notes for next agent: `src/lead_sla_agent/workers/queue.py` imports `redis.asyncio`; sync Redis imports are covered by `tests/unit/test_async_redis.py`.

### 2026-05-19 - T07 - Lead Records and Transcript State

- Scope: `src/lead_sla_agent/intake/lead_service.py`, `src/lead_sla_agent/db/lead_repository.py`, `src/lead_sla_agent/db/transcript_repository.py`, `tests/integration/test_lead_records.py`
- Why this work happened: T07 required normalized inbound events to create lead/conversation state, append transcript records, and enforce tenant-scoped repository reads.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_lead_records.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 21 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T08 SLA Timers and Retry Queue
- Notes for next agent: transcript records store content hashes and redacted previews only; local repository reads return `None` across tenant boundaries.

### 2026-05-19 - T06 - Inbound Webhook Intake

- Scope: `src/lead_sla_agent/api/webhooks.py`, `src/lead_sla_agent/intake/schemas.py`, `src/lead_sla_agent/intake/signatures.py`, `src/lead_sla_agent/intake/normalizer.py`, `tests/integration/test_webhook_intake.py`
- Why this work happened: T06 required signed public webhook intake, event normalization, invalid-signature rejection, and source-event idempotency.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_webhook_intake.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 18 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T07 Lead Records and Transcript State
- Notes for next agent: the route writes through an injectable store; local tests use `InMemoryWebhookStore` to verify row-count and replay behavior without a live PostgreSQL connection.

### 2026-05-19 - Phase 1 Review - Foundation

- Scope: T01-T05, `docs/audit/PHASE1_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`
- Why this work happened: Phase 1 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 15 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T06 Inbound Webhook Intake
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-19 - T05 - Observability and Audit Baseline

- Scope: `src/lead_sla_agent/observability/`, `src/lead_sla_agent/db/audit.py`, `tests/unit/test_tracing_contract.py`, `tests/unit/test_pii_scrubber.py`, `tests/unit/test_audit_events.py`
- Why this work happened: T05 required shared tracing, structured PII-scrubbed logging, metrics helpers, and append-only audit writing.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_tracing_contract.py tests/unit/test_pii_scrubber.py tests/unit/test_audit_events.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 15 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: complete Phase 1 review, then continue to T06
- Notes for next agent: audit repository exposes only `append` publicly and sets tenant context before inserting.

### 2026-05-19 - T04 - Database Models and Tenant Context

- Scope: `alembic/`, `src/lead_sla_agent/db/`, `tests/unit/test_db_models.py`, `tests/unit/test_tenant_context.py`, `tests/unit/test_sql_safety.py`
- Why this work happened: T04 required initial SQLAlchemy/Alembic schema declarations and repository helpers that enforce transaction-scoped tenant context before tenant-scoped queries.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_db_models.py tests/unit/test_tenant_context.py tests/unit/test_sql_safety.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 12 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Follow-ups: continue to T05 Observability and Audit Baseline
- Notes for next agent: tenant-scoped repository reads call `SET LOCAL app.tenant_id = :tenant_id` before query execution; no live database is required for the T04 tests.

### 2026-05-19 - T03 - First Smoke Tests

- Scope: `src/lead_sla_agent/api/app.py`, `src/lead_sla_agent/observability/pii.py`, `tests/integration/test_health.py`, `tests/unit/test_test_layout.py`
- Why this work happened: T03 required service smoke tests for app creation, health response shape, PII-safe health behavior, unit/integration layout, and ruff configuration.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_health.py tests/unit/test_test_layout.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 9 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Follow-ups: continue to T04 Database Models and Tenant Context
- Notes for next agent: health returns only `{"status": "ok"}` and application code does not log on health checks.

### 2026-05-19 - T02 - CI Setup

- Scope: `tests/unit/test_ci_workflow.py`
- Why this work happened: T02 required tests that verify the GitHub Actions workflow has lint, format, test, PostgreSQL, Redis, health checks, and safe placeholder runtime environment values.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_ci_workflow.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 6 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Follow-ups: continue to T03 First Smoke Tests
- Notes for next agent: existing `.github/workflows/ci.yml` already satisfied T02, so no workflow behavior changed.

### 2026-05-19 - T01 - Project Skeleton

- Scope: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.gitignore`, `src/lead_sla_agent/`, `tests/unit/test_project_skeleton.py`
- Why this work happened: T01 required a Python 3.12/FastAPI package skeleton, settings loader, dependency manifests, and stable module layout.
- Decisions applied: none
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_project_skeleton.py -q --tb=short` -> 3 passed; `.venv/bin/python -m pytest tests/ -q --tb=short` -> 3 passed; `.venv/bin/ruff check src/lead_sla_agent tests` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Follow-ups: continue to T02 CI Setup
- Notes for next agent: baseline before T01 was 0 passing tests because no `tests/` tree existed. Added `.gitignore` outside the T01 file list to satisfy the contract requirement that `.env` files are ignored and to exclude the local `.venv` used for verification.

### 2026-05-19 - Bootstrap - Phase 1 Package

- Scope: `docs/`, `.github/workflows/ci.yml`
- Why this work happened: `/bootstrap-new` was run for a new Lead Response SLA Agent repository.
- Decisions applied: `D-001`, `D-002`, `D-003`, `D-004`, `D-005`, `D-006`
- Evidence collected: structural checks pending via Phase 1 Validator
- Follow-ups: start T01 by asking Codex to follow `docs/prompts/ORCHESTRATOR.md`
- Notes for next agent: active profiles are RAG, Tool-Use, and Agentic; keep runtime at T1 unless an ADR justifies escalation. There is no Claude runtime; implement directly in Codex without calling `codex exec`.

### 2026-05-19 - Workflow Adjustment - Codex-Only Execution

- Scope: `docs/prompts/ORCHESTRATOR.md`, `docs/CODEX_PROMPT.md`, `docs/IMPLEMENTATION_CONTRACT.md`, `docs/DECISION_LOG.md`, `.claude/`
- Why this work happened: The project will be operated only through Codex, so Claude commands and `codex exec` invocations from inside Codex are not part of the workflow.
- Decisions applied: `D-006`
- Evidence collected: text search for active Claude/`codex exec` references in project docs
- Follow-ups: use the Codex-native orchestrator for T01
- Notes for next agent: verification by the same Codex session is allowed, but independent review must be a fresh Codex session or human review.

### 2026-05-19 - Workflow Adjustment - Remove Codex CLI Invocation Path

- Scope: `docs/`, `prompts/ORCHESTRATOR.md`, `prompts/STRATEGIST.md`, `PLAYBOOK.md`, `hooks/`, `templates/skills/simplification_skill.md`
- Why this work happened: User clarified that Codex is the executor, so Codex must not be called through `exec`.
- Decisions applied: `D-006`
- Evidence collected: text search for active instructions that invoke Codex through `exec`; removed `hooks/enforce_codex_exec.sh` because it enforced the opposite workflow.
- Follow-ups: run Phase 1 validator after any further workflow-policy changes.
- Notes for next agent: normal shell commands for project tooling are allowed; invoking Codex from inside Codex is not.

### 2026-05-19 - Workflow Adjustment - Nonstop Development Loop

- Scope: `docs/prompts/ORCHESTRATOR.md`, `docs/IMPLEMENTATION_CONTRACT.md`, `docs/CODEX_PROMPT.md`, `docs/DECISION_LOG.md`, `README.md`, `PLAYBOOK.md`
- Why this work happened: User clarified that development must not pause between phases; Codex should follow the loop continuously.
- Decisions applied: `D-008`
- Evidence collected: docs now define phase boundaries as checkpoints, not default pause points, and list explicit stop conditions.
- Follow-ups: none
- Notes for next agent: continue task-by-task and phase-by-phase until a stop condition exists or the task graph is complete.

### 2026-05-19 - RAG Reference - Dream Motif Interpreter

- Scope: `docs/RAG_REFERENCE.md`, `docs/ARCHITECTURE.md`, `docs/tasks.md`, `docs/retrieval_eval.md`, `docs/DECISION_LOG.md`, `docs/EVIDENCE_INDEX.md`
- Why this work happened: User approved using `https://github.com/ashishki/Dream_Motif_Interpreter` as a RAG reference.
- Decisions applied: `D-007`
- Evidence collected: local read of cloned reference repo paths `app/retrieval/types.py`, `app/retrieval/ingestion.py`, `app/retrieval/query.py`, `docs/retrieval_eval.md`, and pgvector migrations
- Follow-ups: T09/T10 should consult `docs/RAG_REFERENCE.md` before implementing RAG
- Notes for next agent: reuse patterns only; do not copy single-user assumptions. Tenant isolation and PII policy override the reference.

### 2026-05-19 - RAG Eval Discipline - Retrieval Quality Gate

- Scope: `docs/retrieval_eval.md`, `docs/IMPLEMENTATION_CONTRACT.md`, `docs/tasks.md`, `docs/RAG_REFERENCE.md`
- Why this work happened: User asked to bring over the RAG evaluation principle from Dream Motif Interpreter.
- Decisions applied: `D-007`
- Evidence collected: `docs/retrieval_eval.md` now requires Date, Eval Source, Corpus version, Dataset, Metrics, Root cause, Result, and Notes for eval history rows
- Follow-ups: T10 must establish the first valid baseline row; T16 must enforce active profile eval gates in CI
- Notes for next agent: do not mark RAG tasks complete with "tests passed" alone. Retrieval quality, answer quality, and no-answer behavior are separate checks.
