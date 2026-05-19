# CODEX_PROMPT.md

Version: 1.0
Date: 2026-05-19
Phase: 6

This file is the single source of truth for current implementation state. Update it before phase boundaries and before handing a task to Codex when state changes.

Execution mode: Codex-only. There is no Claude Code runtime for this project, and Codex must not invoke Codex through `codex exec` or any nested Codex CLI call.

---

## Current State

- Phase: 6
- Baseline: 58 passing tests (`.venv/bin/python -m pytest tests/ -q --tb=short`)
- Ruff: passing (`.venv/bin/ruff check src/lead_sla_agent tests`; `.venv/bin/ruff format --check src/lead_sla_agent tests`)
- Last CI: workflow configured, not yet run remotely
- Last updated: 2026-05-19
- Execution mode: Codex-only, direct task execution
- Development cadence: nonstop loop across phases unless a stop condition exists
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

All tasks complete

Task digest:
- Completed task graph T01-T18.
- Latest baseline: 58 passing tests.
- Latest phase review: `docs/audit/PHASE6_REVIEW.md`.
- No open findings.

---

## Fix Queue

empty

---

## Open Findings

none

---

## Completed Tasks

T01: Project Skeleton

- Completed: 2026-05-19
- Files: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.gitignore`, `src/lead_sla_agent/`, `tests/unit/test_project_skeleton.py`
- Acceptance evidence:
  - `tests/unit/test_project_skeleton.py::test_package_entrypoint_imports`
  - `tests/unit/test_project_skeleton.py::test_settings_load_required_values`
  - `tests/unit/test_project_skeleton.py::test_expected_modules_exist`
- Verification:
  - `.venv/bin/python -m pytest tests/unit/test_project_skeleton.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 3 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Notes: `.gitignore` was added as adjacent support because the implementation contract requires `.env` files to be ignored and local verification used `.venv`.

T02: CI Setup

- Completed: 2026-05-19
- Files: `tests/unit/test_ci_workflow.py`
- Acceptance evidence:
  - `tests/unit/test_ci_workflow.py::test_ci_workflow_has_required_steps`
  - `tests/unit/test_ci_workflow.py::test_ci_workflow_declares_required_services`
  - `tests/unit/test_ci_workflow.py::test_ci_workflow_sets_required_test_env`
- Verification:
  - `.venv/bin/python -m pytest tests/unit/test_ci_workflow.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 6 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Notes: existing `.github/workflows/ci.yml` already met the acceptance criteria; T02 added coverage without changing workflow behavior.

T03: First Smoke Tests

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/api/app.py`, `src/lead_sla_agent/observability/pii.py`, `tests/integration/test_health.py`, `tests/unit/test_test_layout.py`
- Acceptance evidence:
  - `tests/integration/test_health.py::test_health_returns_ok_without_pii`
  - `tests/unit/test_test_layout.py::test_unit_and_integration_tests_exist`
  - `tests/unit/test_test_layout.py::test_ruff_commands_declared_in_pyproject`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_health.py tests/unit/test_test_layout.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 9 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Notes: health endpoint returns only `{"status": "ok"}` and emits no application logs.

T04: Database Models and Tenant Context

- Completed: 2026-05-19
- Files: `alembic/env.py`, `alembic/versions/0001_initial_schema.py`, `src/lead_sla_agent/db/base.py`, `src/lead_sla_agent/db/models.py`, `src/lead_sla_agent/db/repositories.py`, `src/lead_sla_agent/db/tenant.py`, `tests/unit/test_db_models.py`, `tests/unit/test_tenant_context.py`, `tests/unit/test_sql_safety.py`
- Acceptance evidence:
  - `tests/unit/test_db_models.py::test_initial_tables_declared`
  - `tests/unit/test_tenant_context.py::test_repository_requires_tenant_context`
  - `tests/unit/test_sql_safety.py::test_repository_sql_uses_named_parameters`
- Verification:
  - `.venv/bin/python -m pytest tests/unit/test_db_models.py tests/unit/test_tenant_context.py tests/unit/test_sql_safety.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 12 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: tenant-scoped repository reads call `SET LOCAL app.tenant_id = :tenant_id` before query execution.

T05: Observability and Audit Baseline

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/observability/tracing.py`, `src/lead_sla_agent/observability/logging.py`, `src/lead_sla_agent/observability/metrics.py`, `src/lead_sla_agent/observability/pii.py`, `src/lead_sla_agent/db/audit.py`, `tests/unit/test_tracing_contract.py`, `tests/unit/test_pii_scrubber.py`, `tests/unit/test_audit_events.py`
- Acceptance evidence:
  - `tests/unit/test_tracing_contract.py::test_shared_tracing_import_contract`
  - `tests/unit/test_pii_scrubber.py::test_pii_values_are_not_logged`
  - `tests/unit/test_audit_events.py::test_audit_repository_append_only_interface`
- Verification:
  - `.venv/bin/python -m pytest tests/unit/test_tracing_contract.py tests/unit/test_pii_scrubber.py tests/unit/test_audit_events.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 15 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: verification pass found no P0/P1/P2 findings; independent review was not performed.

T06: Inbound Webhook Intake

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/api/webhooks.py`, `src/lead_sla_agent/intake/schemas.py`, `src/lead_sla_agent/intake/signatures.py`, `src/lead_sla_agent/intake/normalizer.py`, `tests/integration/test_webhook_intake.py`
- Acceptance evidence:
  - `tests/integration/test_webhook_intake.py::test_valid_signed_webhook_persists_provider_event`
  - `tests/integration/test_webhook_intake.py::test_invalid_signature_creates_no_rows`
  - `tests/integration/test_webhook_intake.py::test_replayed_event_is_idempotent`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_webhook_intake.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 18 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: webhook route is public but verifies HMAC before writing through an injectable store; local integration tests use `InMemoryWebhookStore`.

T07: Lead Records and Transcript State

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/intake/lead_service.py`, `src/lead_sla_agent/db/lead_repository.py`, `src/lead_sla_agent/db/transcript_repository.py`, `tests/integration/test_lead_records.py`
- Acceptance evidence:
  - `tests/integration/test_lead_records.py::test_normalized_event_creates_lead_and_conversation`
  - `tests/integration/test_lead_records.py::test_transcript_rows_store_redacted_preview`
  - `tests/integration/test_lead_records.py::test_lead_repository_enforces_tenant_scope`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_lead_records.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 21 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: local repositories enforce tenant-scoped reads and transcript records store hashes plus redacted previews, not raw content.

T08: SLA Timers and Retry Queue

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/workers/queue.py`, `src/lead_sla_agent/workers/sla.py`, `src/lead_sla_agent/workers/retries.py`, `tests/integration/test_sla_queue.py`, `tests/unit/test_async_redis.py`
- Acceptance evidence:
  - `tests/integration/test_sla_queue.py::test_sla_timer_records_breach`
  - `tests/integration/test_sla_queue.py::test_retry_exhaustion_creates_review_task`
  - `tests/unit/test_async_redis.py::test_only_async_redis_imported`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_sla_queue.py tests/unit/test_async_redis.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 24 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: retry exhaustion creates one human-review task and repeated timer/retry delivery is idempotent.

T09: Knowledge Ingestion Pipeline

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/retrieval/documents.py`, `src/lead_sla_agent/retrieval/chunking.py`, `src/lead_sla_agent/retrieval/embeddings.py`, `src/lead_sla_agent/retrieval/ingestion.py`, `tests/integration/test_retrieval_ingestion.py`, `tests/eval/test_retrieval_eval.py`, `docs/retrieval_eval.md`, `docs/DECISION_LOG.md`
- Acceptance evidence:
  - `tests/integration/test_retrieval_ingestion.py::test_markdown_faq_ingestion_stores_versioned_chunks`
  - `tests/integration/test_retrieval_ingestion.py::test_unchanged_source_ingestion_is_idempotent`
  - `tests/eval/test_retrieval_eval.py::test_retrieval_eval_metadata_initialized`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_retrieval_ingestion.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 3 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 27 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: RAG eval metadata initialized with `local-hash-embedding-v1`, `rag-index-v1`, `markdown-heading-v1`, and seed dataset path; retrieval quality metrics remain pending T10.

T10: Query-Time Retrieval and Insufficient Evidence

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/retrieval/query.py`, `src/lead_sla_agent/retrieval/evidence.py`, `src/lead_sla_agent/retrieval/eval.py`, `tests/integration/test_retrieval_query.py`, `tests/eval/test_retrieval_eval.py`, `tests/eval/fixtures/retrieval_seed.json`, `docs/retrieval_eval.md`
- Acceptance evidence:
  - `tests/integration/test_retrieval_query.py::test_retrieval_is_tenant_scoped`
  - `tests/integration/test_retrieval_query.py::test_unsupported_query_creates_insufficient_evidence_handoff`
  - `tests/eval/test_retrieval_eval.py::test_retrieval_eval_computes_seed_metrics`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_retrieval_query.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 4 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 30 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
- Notes: retrieval baseline established: hit@3=1.00; hit@5=1.00; MRR=1.00; citation_precision=1.00; no-answer accuracy=1.00; retrieval_p95_latency_ms<1 local.

T11: Tool Catalog and Unsafe-Action Gates

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/tools/catalog.py`, `src/lead_sla_agent/tools/schemas.py`, `src/lead_sla_agent/tools/safety.py`, `src/lead_sla_agent/tools/executor.py`, `tests/unit/test_tool_catalog.py`, `tests/unit/test_tool_safety.py`, `tests/eval/test_tool_eval.py`, `docs/tool_eval.md`
- Acceptance evidence:
  - `tests/unit/test_tool_catalog.py::test_registered_tools_expose_contract_fields`
  - `tests/unit/test_tool_catalog.py::test_write_tools_require_idempotency_key`
  - `tests/unit/test_tool_safety.py::test_unsafe_message_send_routes_to_human_review`
  - `tests/eval/test_tool_eval.py::test_tool_eval_metadata_initialized`
- Verification:
  - `.venv/bin/python -m pytest tests/unit/test_tool_catalog.py tests/unit/test_tool_safety.py tests/eval/test_tool_eval.py -q --tb=short` -> 4 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 34 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Notes: side-effecting tools require idempotency keys and unsafe message sends route to human review before provider execution.

T12: Provider Adapters

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/tools/messaging.py`, `src/lead_sla_agent/tools/calendar.py`, `src/lead_sla_agent/tools/crm.py`, `src/lead_sla_agent/tools/lead_history.py`, `src/lead_sla_agent/operator/review_queue.py`, `tests/integration/test_provider_adapters.py`, `tests/eval/test_tool_eval.py`, `docs/tool_eval.md`
- Acceptance evidence:
  - `tests/integration/test_provider_adapters.py::test_fake_messaging_adapter_records_send_result`
  - `tests/integration/test_provider_adapters.py::test_booking_requires_fresh_slot_lookup`
  - `tests/integration/test_provider_adapters.py::test_crm_write_is_idempotent`
  - `tests/eval/test_tool_eval.py::test_tool_eval_records_runtime_scenarios`
- Verification:
  - `.venv/bin/python -m pytest tests/integration/test_provider_adapters.py tests/eval/test_tool_eval.py -q --tb=short` -> 5 passed
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 38 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
- Notes: fake adapters require no real provider credentials; CRM writes are idempotent by lead ID.

T13: Bounded Conversation Loop

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/conversation/state.py`, `src/lead_sla_agent/conversation/policy.py`, `src/lead_sla_agent/conversation/loop.py`, `src/lead_sla_agent/conversation/model_io.py`, `tests/integration/test_conversation_loop.py`, `tests/eval/test_agent_eval.py`, `docs/agent_eval.md`
- Acceptance evidence: `tests/integration/test_conversation_loop.py`, `tests/eval/test_agent_eval.py`
- Verification: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 42 passed; ruff lint/format passed
- Notes: bounded runtime records explicit termination reasons and cannot continue beyond max-turn budget.

T14: Human Review Queue and Operator Actions

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/operator/api.py`, `src/lead_sla_agent/operator/auth.py`, `src/lead_sla_agent/operator/review_queue.py`, `src/lead_sla_agent/operator/outcomes.py`, `tests/integration/test_operator_review.py`
- Acceptance evidence: `tests/integration/test_operator_review.py`
- Verification: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 46 passed; ruff lint/format passed
- Notes: operator routes require bearer auth before returning review or outcome data.

T15: End-to-End Lead Workflow

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/intake/lead_service.py`, `src/lead_sla_agent/conversation/loop.py`, `src/lead_sla_agent/workers/outbound.py`, `tests/integration/test_end_to_end_workflow.py`
- Acceptance evidence: `tests/integration/test_end_to_end_workflow.py`
- Verification: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 49 passed; ruff lint/format passed
- Notes: supported FAQ path sends through fake messaging; regulated-advice path creates human review without provider send.

T16: Active Profile Eval Gates in CI

- Completed: 2026-05-19
- Files: `.github/workflows/ci.yml`, `tests/unit/test_ci_eval_gates.py`, `tests/eval/test_eval_artifacts.py`, `docs/retrieval_eval.md`, `docs/tool_eval.md`, `docs/agent_eval.md`, `docs/EVIDENCE_INDEX.md`
- Acceptance evidence: `tests/unit/test_ci_eval_gates.py`, `tests/eval/test_eval_artifacts.py`
- Verification: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 52 passed; ruff lint/format passed
- Notes: CI now has separate Retrieval, Tool-use, and Agent eval steps.

T17: Metrics, Health, and NFR Baseline

- Completed: 2026-05-19
- Files: `src/lead_sla_agent/observability/metrics.py`, `src/lead_sla_agent/api/health.py`, `tests/integration/test_metrics.py`, `tests/integration/test_health.py`, `tests/unit/test_nfr_doc.py`, `docs/nfr.md`
- Acceptance evidence: `tests/integration/test_metrics.py`, `tests/integration/test_health.py`, `tests/unit/test_nfr_doc.py`
- Verification: `.venv/bin/python -m pytest tests/ -q --tb=short` -> 55 passed; ruff lint/format passed
- Notes: workflow emits first-response, SLA, retrieval, tool-call, and termination metrics.

T18: Deployment and Operator Runbook

- Completed: 2026-05-19
- Files: `Dockerfile`, `compose.yml`, `docs/runbook.md`, `tests/unit/test_deployment_docs.py`
- Acceptance evidence: `tests/unit/test_deployment_docs.py`
- Verification:
  - `.venv/bin/python -m pytest tests/ -q --tb=short` -> 58 passed
  - `.venv/bin/ruff check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff format --check src/lead_sla_agent tests` -> passed
  - `.venv/bin/ruff check alembic && .venv/bin/ruff format --check alembic` -> passed
  - `docker-compose -f compose.yml config` -> passed
- Notes: Compose defines API, worker, PostgreSQL, and Redis services; runbook documents secrets policy.

---

## Profile State: RAG

- RAG Status: ON
- Active corpora: pilot tenant approved text knowledge base
- Retrieval baseline: T10 seed baseline established; hit@3=1.00, hit@5=1.00, MRR=1.00, citation_precision=1.00, no-answer accuracy=1.00
- Open retrieval findings: none
- Index schema version: rag-index-v1
- Pending reindex actions: none
- Retrieval-related next tasks: T09, T10, T13, T15, T16
- Retrieval-driven tasks: none

---

## Tool-Use State

- Tool-Use Profile: ON
- Registered tool schemas: `tool-schema-v1` for send_message, create_or_update_lead, lookup_available_slots, book_slot, lookup_lead_history, create_human_review_task
- Unsafe-action guardrails: human gate required for unsafe message categories, explicit customer acceptance required for booking, idempotency required for write tools
- Open tool findings: none

---

## Agentic State

- Agentic Profile: ON
- Active agent roles: bounded lead qualification conversation runtime
- Loop termination contract version: `agent-loop-v1`
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

- Profile: RAG, Tool-Use, Agentic
- Task: T16
- Date: 2026-05-19
- Eval Source: `.venv/bin/python -m pytest tests/eval/ -q --tb=short`
- Metric(s): retrieval hit/no-answer baseline, tool safety/idempotency baseline, agent allowed-action/termination baseline
- Score: pass
- Baseline: established
- Delta: n/a
- Regression: No

### Open Evaluation Issues

none

### Evaluation History

No evaluations have run yet.

---

## Phase History

### Phase 1

- Completed: 2026-05-19
- Summary: package skeleton, CI workflow coverage, health smoke tests, initial database schema and tenant context, shared observability helpers, and append-only audit writer.
- Baseline: 15 passing tests
- Review artifact: `docs/audit/PHASE1_REVIEW.md`
- Findings: none

### Phase 2

- Completed: 2026-05-19
- Summary: signed webhook intake, normalized lead/transcript state, tenant-scoped local repositories, SLA breach marking, retry exhaustion fallback, and async Redis queue facade.
- Baseline: 24 passing tests
- Review artifact: `docs/audit/PHASE2_REVIEW.md`
- Findings: none

### Phase 3

- Completed: 2026-05-19
- Summary: text-only knowledge ingestion, deterministic local embedding adapter, tenant-scoped query-time retrieval, insufficient-evidence handoff, and seed retrieval metrics baseline.
- Baseline: 30 passing tests
- Review artifact: `docs/audit/PHASE3_REVIEW.md`
- Findings: none

### Phase 4

- Completed: 2026-05-19
- Summary: versioned tool catalog, unsafe-action gate, idempotency enforcement, fake provider adapters, and tool eval runtime scenarios.
- Baseline: 38 passing tests
- Review artifact: `docs/audit/PHASE4_REVIEW.md`
- Findings: none

### Phase 5

- Completed: 2026-05-19
- Summary: bounded conversation runtime, operator review API, outcome labels, and end-to-end lead workflow over retrieval/tool/provider fakes.
- Baseline: 49 passing tests
- Review artifact: `docs/audit/PHASE5_REVIEW.md`
- Findings: none

### Phase 6

- Completed: 2026-05-19
- Summary: active profile eval CI gates, observability/NFR baseline, health dependency status, Docker Compose deployment, and operator runbook.
- Baseline: 58 passing tests
- Review artifact: `docs/audit/PHASE6_REVIEW.md`
- Findings: none

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
11. Continue automatically to the next task and next phase when verification is green and no stop condition exists.
12. Stop only for unresolved P0/P1 findings, failing checks, eval regressions, architecture/runtime/governance/profile/security-boundary changes, missing required evidence, or explicit user pause/stop instruction.
13. When done, return `IMPLEMENTATION_RESULT: DONE` with the new baseline and what changed.
14. When blocked, return `IMPLEMENTATION_RESULT: BLOCKED` with the exact blocker and the smallest unblock step.
