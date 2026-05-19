# Tasks - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Status: Draft

Every task follows the schema in `templates/tasks_schema.md`. Task tags describe capability ownership. A task with a profile trigger tag is not complete until the matching eval artifact is updated.

---

## Phase 1 - Foundation

Goal: create a testable Python/FastAPI skeleton with CI, config, health, and baseline safety rules.

## T01: Project Skeleton

Owner:      codex
Phase:      1
Type:       none
Depends-On: none

Objective: |
  Create the Python package skeleton, dependency files, local settings loader, FastAPI app entrypoint, and directory layout described in docs/ARCHITECTURE.md so future tasks have stable import paths and a runnable service shell.

Acceptance-Criteria:
  - id: AC-1
    description: "Running `python -m lead_sla_agent` starts an ASGI app object import path without raising an import error. Verified by tests/unit/test_project_skeleton.py::test_package_entrypoint_imports."
    test: "tests/unit/test_project_skeleton.py::test_package_entrypoint_imports"
  - id: AC-2
    description: "`Settings` loads `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, and `WEBHOOK_SHARED_SECRET` from environment variables with test defaults. Verified by tests/unit/test_project_skeleton.py::test_settings_load_required_values."
    test: "tests/unit/test_project_skeleton.py::test_settings_load_required_values"
  - id: AC-3
    description: "The package includes `api`, `conversation`, `db`, `intake`, `observability`, `operator`, `retrieval`, `tools`, and `workers` modules. Verified by tests/unit/test_project_skeleton.py::test_expected_modules_exist."
    test: "tests/unit/test_project_skeleton.py::test_expected_modules_exist"

Files:
  - pyproject.toml
  - requirements.txt
  - requirements-dev.txt
  - src/lead_sla_agent/__init__.py
  - src/lead_sla_agent/__main__.py
  - src/lead_sla_agent/config.py
  - src/lead_sla_agent/api/app.py
  - tests/unit/test_project_skeleton.py

Context-Refs:
  - docs/ARCHITECTURE.md#file-layout
  - docs/ARCHITECTURE.md#runtime-contract

Notes: |
  Use Python 3.12, FastAPI, Pydantic v2, pytest, pytest-asyncio, httpx, ruff, SQLAlchemy 2.x, Alembic, asyncpg, redis, and OpenTelemetry-compatible dependencies. Do not add provider SDKs until the matching integration task.

## T02: CI Setup

Owner:      codex
Phase:      1
Type:       none
Depends-On: T01

Objective: |
  Make GitHub Actions install the project, run ruff lint, run ruff format check, start required PostgreSQL and Redis services, and execute the test suite with safe placeholder environment values.

Acceptance-Criteria:
  - id: AC-1
    description: ".github/workflows/ci.yml is parseable YAML and contains steps named `Lint`, `Format check`, and `Run tests`. Verified by tests/unit/test_ci_workflow.py::test_ci_workflow_has_required_steps."
    test: "tests/unit/test_ci_workflow.py::test_ci_workflow_has_required_steps"
  - id: AC-2
    description: "The CI workflow declares PostgreSQL and Redis service containers with health checks. Verified by tests/unit/test_ci_workflow.py::test_ci_workflow_declares_required_services."
    test: "tests/unit/test_ci_workflow.py::test_ci_workflow_declares_required_services"
  - id: AC-3
    description: "The test step provides placeholder values for all required runtime contract variables listed for local CI. Verified by tests/unit/test_ci_workflow.py::test_ci_workflow_sets_required_test_env."
    test: "tests/unit/test_ci_workflow.py::test_ci_workflow_sets_required_test_env"

Files:
  - .github/workflows/ci.yml
  - tests/unit/test_ci_workflow.py

Context-Refs:
  - docs/ARCHITECTURE.md#runtime-contract
  - docs/IMPLEMENTATION_CONTRACT.md#ci-gate

Notes: |
  CI must remain runnable after T01 and T03. Use only test placeholder strings, not real provider credentials.

## T03: First Smoke Tests

Owner:      codex
Phase:      1
Type:       none
Depends-On: T01, T02

Objective: |
  Add the first service smoke tests for app creation, health response shape, and PII-safe health logging so the baseline can be recorded before feature work starts.

Acceptance-Criteria:
  - id: AC-1
    description: "`GET /health` returns HTTP 200 with JSON body containing `status: ok` and no PII fields. Verified by tests/integration/test_health.py::test_health_returns_ok_without_pii."
    test: "tests/integration/test_health.py::test_health_returns_ok_without_pii"
  - id: AC-2
    description: "The test suite can run with `python -m pytest tests/ -q` and includes at least one unit test and one integration test. Verified by tests/unit/test_test_layout.py::test_unit_and_integration_tests_exist."
    test: "tests/unit/test_test_layout.py::test_unit_and_integration_tests_exist"
  - id: AC-3
    description: "Ruff check and ruff format check pass for `src/lead_sla_agent` and `tests`. Verified by tests/unit/test_test_layout.py::test_ruff_commands_declared_in_pyproject."
    test: "tests/unit/test_test_layout.py::test_ruff_commands_declared_in_pyproject"

Files:
  - src/lead_sla_agent/api/app.py
  - src/lead_sla_agent/observability/pii.py
  - tests/integration/test_health.py
  - tests/unit/test_test_layout.py

Context-Refs:
  - docs/IMPLEMENTATION_CONTRACT.md#pii-policy
  - docs/ARCHITECTURE.md#observability

Notes: |
  After this task passes, update docs/CODEX_PROMPT.md with the first passing baseline.

## T04: Database Models and Tenant Context

Owner:      codex
Phase:      1
Type:       none
Depends-On: T03

Objective: |
  Define the initial PostgreSQL schema for tenants, leads, conversations, messages, audit events, and provider events with repository helpers that enforce tenant context before tenant-scoped queries.

Acceptance-Criteria:
  - id: AC-1
    description: "Alembic metadata includes tenant, lead, conversation, message, audit_event, and provider_event tables with UUID primary keys and created_at timestamps. Verified by tests/unit/test_db_models.py::test_initial_tables_declared."
    test: "tests/unit/test_db_models.py::test_initial_tables_declared"
  - id: AC-2
    description: "Repository calls touching tenant-scoped tables require a tenant ID argument and issue tenant context before query execution. Verified by tests/unit/test_tenant_context.py::test_repository_requires_tenant_context."
    test: "tests/unit/test_tenant_context.py::test_repository_requires_tenant_context"
  - id: AC-3
    description: "SQL helper tests reject f-string, percent-format, or concatenated SQL examples in repository modules. Verified by tests/unit/test_sql_safety.py::test_repository_sql_uses_named_parameters."
    test: "tests/unit/test_sql_safety.py::test_repository_sql_uses_named_parameters"

Files:
  - alembic/env.py
  - alembic/versions/0001_initial_schema.py
  - src/lead_sla_agent/db/base.py
  - src/lead_sla_agent/db/models.py
  - src/lead_sla_agent/db/repositories.py
  - src/lead_sla_agent/db/tenant.py
  - tests/unit/test_db_models.py
  - tests/unit/test_tenant_context.py
  - tests/unit/test_sql_safety.py

Context-Refs:
  - docs/IMPLEMENTATION_CONTRACT.md#sql-safety
  - docs/IMPLEMENTATION_CONTRACT.md#multi-tenant-systems

Notes: |
  Use `SET LOCAL app.tenant_id = :tid` or an equivalent transaction-scoped tenant context. Do not use session-level `SET`.

## T05: Observability and Audit Baseline

Owner:      codex
Phase:      1
Type:       none
Depends-On: T03, T04

Objective: |
  Add shared tracing, structured PII-scrubbed logging, metrics helpers, and append-only audit event writing used by intake, retrieval, tool, and conversation tasks.

Acceptance-Criteria:
  - id: AC-1
    description: "All tracing imports in `src/lead_sla_agent` resolve to `src/lead_sla_agent/observability/tracing.py::get_tracer`. Verified by tests/unit/test_tracing_contract.py::test_shared_tracing_import_contract."
    test: "tests/unit/test_tracing_contract.py::test_shared_tracing_import_contract"
  - id: AC-2
    description: "Log records containing name, phone, email, or message text are emitted with hashed identifiers or redacted values. Verified by tests/unit/test_pii_scrubber.py::test_pii_values_are_not_logged."
    test: "tests/unit/test_pii_scrubber.py::test_pii_values_are_not_logged"
  - id: AC-3
    description: "Audit event writes append a new row and do not expose update/delete repository methods. Verified by tests/unit/test_audit_events.py::test_audit_repository_append_only_interface."
    test: "tests/unit/test_audit_events.py::test_audit_repository_append_only_interface"

Files:
  - src/lead_sla_agent/observability/tracing.py
  - src/lead_sla_agent/observability/logging.py
  - src/lead_sla_agent/observability/metrics.py
  - src/lead_sla_agent/observability/pii.py
  - src/lead_sla_agent/db/audit.py
  - tests/unit/test_tracing_contract.py
  - tests/unit/test_pii_scrubber.py
  - tests/unit/test_audit_events.py

Context-Refs:
  - docs/ARCHITECTURE.md#observability
  - docs/IMPLEMENTATION_CONTRACT.md#observability

Notes: |
  This task is a prerequisite for all side-effecting and AI-assisted paths.

---

## Phase 2 - Intake and Lead State

Goal: accept inbound leads safely, create structured lead state, and track SLA timers.

## T06: Inbound Webhook Intake

Owner:      codex
Phase:      2
Type:       none
Depends-On: T04, T05

Objective: |
  Implement signed inbound webhook endpoints and event normalization for website forms and a generic messaging-provider event shape.

Acceptance-Criteria:
  - id: AC-1
    description: "A valid signed webhook request returns HTTP 202 and stores a provider event with source event ID, channel, tenant ID, payload hash, and received timestamp. Verified by tests/integration/test_webhook_intake.py::test_valid_signed_webhook_persists_provider_event."
    test: "tests/integration/test_webhook_intake.py::test_valid_signed_webhook_persists_provider_event"
  - id: AC-2
    description: "An invalid signature returns HTTP 401 and leaves provider_event, lead, conversation, and audit_event row counts unchanged. Verified by tests/integration/test_webhook_intake.py::test_invalid_signature_creates_no_rows."
    test: "tests/integration/test_webhook_intake.py::test_invalid_signature_creates_no_rows"
  - id: AC-3
    description: "Two webhook deliveries with the same source event ID return the same provider event ID and create one lead. Verified by tests/integration/test_webhook_intake.py::test_replayed_event_is_idempotent."
    test: "tests/integration/test_webhook_intake.py::test_replayed_event_is_idempotent"

Files:
  - src/lead_sla_agent/api/webhooks.py
  - src/lead_sla_agent/intake/schemas.py
  - src/lead_sla_agent/intake/signatures.py
  - src/lead_sla_agent/intake/normalizer.py
  - tests/integration/test_webhook_intake.py

Context-Refs:
  - docs/spec.md#feature-area-inbound-lead-intake
  - docs/IMPLEMENTATION_CONTRACT.md#authorization

Notes: |
  Public webhook routes are intentionally unauthenticated but must verify signatures before accepting state-changing input.

## T07: Lead Records and Transcript State

Owner:      codex
Phase:      2
Type:       none
Depends-On: T06

Objective: |
  Create lead, conversation, and transcript repositories that convert normalized inbound events into structured lead state and append transcript messages.

Acceptance-Criteria:
  - id: AC-1
    description: "A normalized inbound message creates a lead with contact fields, source channel, status `new`, and linked conversation. Verified by tests/integration/test_lead_records.py::test_normalized_event_creates_lead_and_conversation."
    test: "tests/integration/test_lead_records.py::test_normalized_event_creates_lead_and_conversation"
  - id: AC-2
    description: "Inbound and outbound transcript rows store role, channel, provider message ID, content hash, and redacted preview. Verified by tests/integration/test_lead_records.py::test_transcript_rows_store_redacted_preview."
    test: "tests/integration/test_lead_records.py::test_transcript_rows_store_redacted_preview"
  - id: AC-3
    description: "Tenant A cannot read Tenant B leads through repository calls. Verified by tests/integration/test_lead_records.py::test_lead_repository_enforces_tenant_scope."
    test: "tests/integration/test_lead_records.py::test_lead_repository_enforces_tenant_scope"

Files:
  - src/lead_sla_agent/intake/lead_service.py
  - src/lead_sla_agent/db/lead_repository.py
  - src/lead_sla_agent/db/transcript_repository.py
  - tests/integration/test_lead_records.py

Context-Refs:
  - docs/ARCHITECTURE.md#security-boundaries

Notes: |
  Transcript text is application data and may be PII. Keep logs and metrics scrubbed.

## T08: SLA Timers and Retry Queue

Owner:      codex
Phase:      2
Type:       none
Depends-On: T07

Objective: |
  Add Redis-backed asynchronous queue helpers for first-response SLA timers, outbound send retries, and provider error fallback to human review.

Acceptance-Criteria:
  - id: AC-1
    description: "SLA timer jobs mark a lead with `sla_breached_at` when no outbound response is confirmed before the configured threshold. Verified by tests/integration/test_sla_queue.py::test_sla_timer_records_breach."
    test: "tests/integration/test_sla_queue.py::test_sla_timer_records_breach"
  - id: AC-2
    description: "Outbound send retries stop after the configured retry limit and create a human-review task. Verified by tests/integration/test_sla_queue.py::test_retry_exhaustion_creates_review_task."
    test: "tests/integration/test_sla_queue.py::test_retry_exhaustion_creates_review_task"
  - id: AC-3
    description: "Async queue modules import `redis.asyncio` and never import synchronous `redis`. Verified by tests/unit/test_async_redis.py::test_only_async_redis_imported."
    test: "tests/unit/test_async_redis.py::test_only_async_redis_imported"

Files:
  - src/lead_sla_agent/workers/queue.py
  - src/lead_sla_agent/workers/sla.py
  - src/lead_sla_agent/workers/retries.py
  - tests/integration/test_sla_queue.py
  - tests/unit/test_async_redis.py

Context-Refs:
  - docs/IMPLEMENTATION_CONTRACT.md#async-redis
  - docs/spec.md#feature-area-fast-acknowledgement-and-sla-tracking

Notes: |
  Timer and retry jobs must be idempotent because queues may deliver more than once.

---

## Phase 3 - Retrieval and Knowledge Grounding

Goal: build text-only RAG ingestion and query-time grounding with measurable no-answer behavior.

## T09: Knowledge Ingestion Pipeline

Owner:      codex
Phase:      3
Type:       rag:ingestion
Depends-On: T04, T05

Objective: |
  Implement the text-only ingestion pipeline that normalizes approved knowledge documents, chunks them by section, embeds chunks through a versioned adapter, and stores tenant-scoped index rows with schema version and freshness metadata.

Acceptance-Criteria:
  - id: AC-1
    description: "Ingesting a markdown FAQ creates chunk rows with tenant ID, source document ID, source title, effective date, content hash, chunk ordinal, and index schema version `rag-index-v1`. Verified by tests/integration/test_retrieval_ingestion.py::test_markdown_faq_ingestion_stores_versioned_chunks."
    test: "tests/integration/test_retrieval_ingestion.py::test_markdown_faq_ingestion_stores_versioned_chunks"
  - id: AC-2
    description: "Re-ingesting unchanged source text does not create duplicate chunks and preserves the existing content hash. Verified by tests/integration/test_retrieval_ingestion.py::test_unchanged_source_ingestion_is_idempotent."
    test: "tests/integration/test_retrieval_ingestion.py::test_unchanged_source_ingestion_is_idempotent"
  - id: AC-3
    description: "`docs/retrieval_eval.md` records embedding model, index schema version, chunking strategy, seed dataset path, and baseline status. Verified by tests/eval/test_retrieval_eval.py::test_retrieval_eval_metadata_initialized."
    test: "tests/eval/test_retrieval_eval.py::test_retrieval_eval_metadata_initialized"

Files:
  - src/lead_sla_agent/retrieval/documents.py
  - src/lead_sla_agent/retrieval/chunking.py
  - src/lead_sla_agent/retrieval/embeddings.py
  - src/lead_sla_agent/retrieval/ingestion.py
  - tests/integration/test_retrieval_ingestion.py
  - tests/eval/test_retrieval_eval.py
  - docs/retrieval_eval.md

Context-Refs:
  - docs/ARCHITECTURE.md#profile-rag
  - docs/IMPLEMENTATION_CONTRACT.md#rag-rules

Notes: |
  Retrieval mode is text-only. Selecting a concrete embedding model updates docs/retrieval_eval.md and docs/DECISION_LOG.md.

Execution-Mode: heavy
Evidence:
  - tests/integration/test_retrieval_ingestion.py
  - tests/eval/test_retrieval_eval.py
  - docs/retrieval_eval.md baseline metadata
Verifier-Focus: |
  Confirm ingestion and query-time retrieval remain separate modules, corpus rows are tenant-scoped, and unchanged source ingestion is idempotent.

## T10: Query-Time Retrieval and Insufficient Evidence

Owner:      codex
Phase:      3
Type:       rag:query
Depends-On: T09

Objective: |
  Implement tenant-scoped query-time retrieval, evidence assembly, score filtering, freshness checks, and the `insufficient_evidence` path used by customer-facing reply drafting.

Acceptance-Criteria:
  - id: AC-1
    description: "Retrieval queries include tenant filtering and never return chunks from another tenant corpus. Verified by tests/integration/test_retrieval_query.py::test_retrieval_is_tenant_scoped."
    test: "tests/integration/test_retrieval_query.py::test_retrieval_is_tenant_scoped"
  - id: AC-2
    description: "Unsupported questions return result status `insufficient_evidence` with no answer text and create a human-review task. Verified by tests/integration/test_retrieval_query.py::test_unsupported_query_creates_insufficient_evidence_handoff."
    test: "tests/integration/test_retrieval_query.py::test_unsupported_query_creates_insufficient_evidence_handoff"
  - id: AC-3
    description: "Retrieval eval computes hit@3, citation precision, no-answer accuracy, and retrieval latency for the seed dataset. Verified by tests/eval/test_retrieval_eval.py::test_retrieval_eval_computes_seed_metrics."
    test: "tests/eval/test_retrieval_eval.py::test_retrieval_eval_computes_seed_metrics"

Files:
  - src/lead_sla_agent/retrieval/query.py
  - src/lead_sla_agent/retrieval/evidence.py
  - src/lead_sla_agent/retrieval/eval.py
  - tests/integration/test_retrieval_query.py
  - tests/eval/test_retrieval_eval.py
  - tests/eval/fixtures/retrieval_seed.json
  - docs/retrieval_eval.md

Context-Refs:
  - docs/ARCHITECTURE.md#profile-rag
  - docs/IMPLEMENTATION_CONTRACT.md#rag-rules

Notes: |
  Do not draft an answer in retrieval code. Return evidence or `insufficient_evidence`; reply drafting belongs to the conversation layer.

Execution-Mode: heavy
Evidence:
  - tests/integration/test_retrieval_query.py
  - tests/eval/test_retrieval_eval.py
  - docs/retrieval_eval.md current metrics
Verifier-Focus: |
  Confirm unsupported queries cannot produce answer text and retrieval metrics are compared against the baseline row.

---

## Phase 4 - Tool Schemas and Integrations

Goal: define versioned tool contracts and safe provider adapters for messaging, CRM, calendar, and review queue side effects.

## T11: Tool Catalog and Unsafe-Action Gates

Owner:      codex
Phase:      4
Type:       tool:schema tool:unsafe
Depends-On: T05, T07

Objective: |
  Implement the versioned tool catalog, input/output schema validation, side-effect classification, idempotency checks, timeout/retry metadata, and unsafe-action gate used before any external side effect is executed.

Acceptance-Criteria:
  - id: AC-1
    description: "Every registered tool exposes name, version, input schema, output schema, side-effect class, idempotency rule, timeout, retry policy, and human-gate rule. Verified by tests/unit/test_tool_catalog.py::test_registered_tools_expose_contract_fields."
    test: "tests/unit/test_tool_catalog.py::test_registered_tools_expose_contract_fields"
  - id: AC-2
    description: "Side-effecting tool calls without a required idempotency key are rejected before provider execution. Verified by tests/unit/test_tool_catalog.py::test_write_tools_require_idempotency_key."
    test: "tests/unit/test_tool_catalog.py::test_write_tools_require_idempotency_key"
  - id: AC-3
    description: "Unsafe message categories create a human-review task instead of calling the provider adapter. Verified by tests/unit/test_tool_safety.py::test_unsafe_message_send_routes_to_human_review."
    test: "tests/unit/test_tool_safety.py::test_unsafe_message_send_routes_to_human_review"
  - id: AC-4
    description: "`docs/tool_eval.md` records tool schema version, registered tools, side-effect classes, and initial eval scenarios. Verified by tests/eval/test_tool_eval.py::test_tool_eval_metadata_initialized."
    test: "tests/eval/test_tool_eval.py::test_tool_eval_metadata_initialized"

Files:
  - src/lead_sla_agent/tools/catalog.py
  - src/lead_sla_agent/tools/schemas.py
  - src/lead_sla_agent/tools/safety.py
  - src/lead_sla_agent/tools/executor.py
  - tests/unit/test_tool_catalog.py
  - tests/unit/test_tool_safety.py
  - tests/eval/test_tool_eval.py
  - docs/tool_eval.md

Context-Refs:
  - docs/ARCHITECTURE.md#profile-tool-use
  - docs/IMPLEMENTATION_CONTRACT.md#tool-use-rules

Notes: |
  MCP-shaped or external tool catalog rows must follow the schema in reference/external_tools_mcp_companion.md if MCP is introduced later.

Execution-Mode: heavy
Evidence:
  - tests/unit/test_tool_catalog.py
  - tests/unit/test_tool_safety.py
  - tests/eval/test_tool_eval.py
  - docs/tool_eval.md
Verifier-Focus: |
  Confirm side effects are explicit, unsafe categories cannot bypass human review, and schema version changes are visible in eval metadata.

## T12: Provider Adapters

Owner:      codex
Phase:      4
Type:       tool:call
Depends-On: T08, T11

Objective: |
  Implement provider adapter interfaces and test doubles for messaging, calendar lookup/booking, CRM/spreadsheet writes, lead-history lookup, and human-review task creation without hardcoding provider credentials.

Acceptance-Criteria:
  - id: AC-1
    description: "Messaging adapter sends a redacted test message through a fake provider and records provider message ID, status, and latency. Verified by tests/integration/test_provider_adapters.py::test_fake_messaging_adapter_records_send_result."
    test: "tests/integration/test_provider_adapters.py::test_fake_messaging_adapter_records_send_result"
  - id: AC-2
    description: "Calendar booking rejects a booking request when no fresh slot lookup exists for the requested slot ID. Verified by tests/integration/test_provider_adapters.py::test_booking_requires_fresh_slot_lookup."
    test: "tests/integration/test_provider_adapters.py::test_booking_requires_fresh_slot_lookup"
  - id: AC-3
    description: "CRM writes use lead ID idempotency and return the existing remote record mapping for duplicate writes. Verified by tests/integration/test_provider_adapters.py::test_crm_write_is_idempotent."
    test: "tests/integration/test_provider_adapters.py::test_crm_write_is_idempotent"
  - id: AC-4
    description: "Tool eval records call success, schema validation pass rate, unsafe-gate pass rate, and timeout scenarios. Verified by tests/eval/test_tool_eval.py::test_tool_eval_records_runtime_scenarios."
    test: "tests/eval/test_tool_eval.py::test_tool_eval_records_runtime_scenarios"

Files:
  - src/lead_sla_agent/tools/messaging.py
  - src/lead_sla_agent/tools/calendar.py
  - src/lead_sla_agent/tools/crm.py
  - src/lead_sla_agent/tools/lead_history.py
  - src/lead_sla_agent/operator/review_queue.py
  - tests/integration/test_provider_adapters.py
  - tests/eval/test_tool_eval.py
  - docs/tool_eval.md

Context-Refs:
  - docs/spec.md#feature-area-tool-use-integrations
  - docs/ARCHITECTURE.md#external-integrations

Notes: |
  Use fake providers in tests. Real provider SDKs require adapter-level environment variables and must not leak credentials into fixtures.

---

## Phase 5 - Conversation Runtime and Human Review

Goal: combine intake, retrieval, tools, and bounded agent policy into a measurable lead qualification workflow.

## T13: Bounded Conversation Loop

Owner:      codex
Phase:      5
Type:       agent:loop agent:termination tool:call rag:query
Depends-On: T08, T10, T12

Objective: |
  Implement the bounded conversation runtime that loads state, extracts lead fields, retrieves evidence when needed, chooses one allowed next action, validates policy/tool constraints, appends audit events, and terminates with a recorded reason.

Acceptance-Criteria:
  - id: AC-1
    description: "For a lead missing required fields, the runtime selects an allowed qualifying question and appends one outbound draft event. Verified by tests/integration/test_conversation_loop.py::test_missing_fields_selects_qualifying_question."
    test: "tests/integration/test_conversation_loop.py::test_missing_fields_selects_qualifying_question"
  - id: AC-2
    description: "For an unsupported policy question, the runtime records termination reason `unsupported_question` and creates a human-review task. Verified by tests/integration/test_conversation_loop.py::test_unsupported_question_terminates_with_handoff."
    test: "tests/integration/test_conversation_loop.py::test_unsupported_question_terminates_with_handoff"
  - id: AC-3
    description: "The runtime stops after `MAX_AUTONOMOUS_TURNS` and records termination reason `budget_exceeded`. Verified by tests/integration/test_conversation_loop.py::test_max_turn_budget_terminates_loop."
    test: "tests/integration/test_conversation_loop.py::test_max_turn_budget_terminates_loop"
  - id: AC-4
    description: "`docs/agent_eval.md` records allowed-action accuracy, termination-rate checks, handoff integrity, and tool-call budget scenarios. Verified by tests/eval/test_agent_eval.py::test_agent_eval_metadata_initialized."
    test: "tests/eval/test_agent_eval.py::test_agent_eval_metadata_initialized"

Files:
  - src/lead_sla_agent/conversation/state.py
  - src/lead_sla_agent/conversation/policy.py
  - src/lead_sla_agent/conversation/loop.py
  - src/lead_sla_agent/conversation/model_io.py
  - tests/integration/test_conversation_loop.py
  - tests/eval/test_agent_eval.py
  - docs/agent_eval.md
  - docs/retrieval_eval.md
  - docs/tool_eval.md

Context-Refs:
  - docs/ARCHITECTURE.md#profile-agentic
  - docs/ARCHITECTURE.md#human-approval-boundaries
  - docs/IMPLEMENTATION_CONTRACT.md#agentic-rules

Notes: |
  This is a bounded runtime loop, not higher-autonomy execution. No shell access, hidden memory, runtime subagents, or toolchain mutation.

Execution-Mode: heavy
Evidence:
  - tests/integration/test_conversation_loop.py
  - tests/eval/test_agent_eval.py
  - docs/agent_eval.md
  - docs/retrieval_eval.md and docs/tool_eval.md updates if behavior changes those profiles
Verifier-Focus: |
  Confirm the loop chooses only allowed actions, updates all affected eval artifacts, and cannot continue after termination conditions.

## T14: Human Review Queue and Operator Actions

Owner:      codex
Phase:      5
Type:       tool:call agent:handoff
Depends-On: T12, T13

Objective: |
  Implement authenticated operator APIs for human-review queue listing, transcript inspection, approval/edit actions, outcome tagging, and safe send after approval.

Acceptance-Criteria:
  - id: AC-1
    description: "Authenticated operators can list review tasks with lead summary, handoff reason, transcript references, evidence IDs, and proposed reply when present. Verified by tests/integration/test_operator_review.py::test_operator_can_list_review_tasks."
    test: "tests/integration/test_operator_review.py::test_operator_can_list_review_tasks"
  - id: AC-2
    description: "Unauthenticated operator API requests return HTTP 401 before accessing lead or transcript data. Verified by tests/integration/test_operator_review.py::test_operator_routes_require_auth."
    test: "tests/integration/test_operator_review.py::test_operator_routes_require_auth"
  - id: AC-3
    description: "Approving a proposed reply records actor ID, timestamp, original draft hash, final message hash, and reason code before sending. Verified by tests/integration/test_operator_review.py::test_approval_records_audit_fields_before_send."
    test: "tests/integration/test_operator_review.py::test_approval_records_audit_fields_before_send"
  - id: AC-4
    description: "Outcome labels are stored on the lead and can be queried by tenant and date range. Verified by tests/integration/test_operator_review.py::test_outcome_labels_are_queryable."
    test: "tests/integration/test_operator_review.py::test_outcome_labels_are_queryable"

Files:
  - src/lead_sla_agent/operator/api.py
  - src/lead_sla_agent/operator/auth.py
  - src/lead_sla_agent/operator/review_queue.py
  - src/lead_sla_agent/operator/outcomes.py
  - tests/integration/test_operator_review.py

Context-Refs:
  - docs/spec.md#feature-area-human-review-and-operator-dashboard
  - docs/IMPLEMENTATION_CONTRACT.md#authorization

Notes: |
  Keep UI optional in v1. A JSON operator API is acceptable if it supports review, approve/edit, and outcome tagging.

## T15: End-to-End Lead Workflow

Owner:      codex
Phase:      5
Type:       agent:loop tool:call rag:query
Depends-On: T13, T14

Objective: |
  Connect the inbound webhook path, lead creation, retrieval, conversation runtime, tool execution, transcript append, and operator escalation into one end-to-end workflow test path.

Acceptance-Criteria:
  - id: AC-1
    description: "A valid inbound lead with a supported FAQ question produces one persisted lead, one retrieved evidence set, one outbound message draft, and one confirmed send through the fake messaging provider. Verified by tests/integration/test_end_to_end_workflow.py::test_supported_question_sends_grounded_reply."
    test: "tests/integration/test_end_to_end_workflow.py::test_supported_question_sends_grounded_reply"
  - id: AC-2
    description: "A valid inbound lead asking for regulated advice produces one persisted lead, no provider send, and one human-review task. Verified by tests/integration/test_end_to_end_workflow.py::test_regulated_advice_creates_review_without_send."
    test: "tests/integration/test_end_to_end_workflow.py::test_regulated_advice_creates_review_without_send"
  - id: AC-3
    description: "The workflow records first-response latency and termination reason for every processed inbound event. Verified by tests/integration/test_end_to_end_workflow.py::test_workflow_records_latency_and_termination_reason."
    test: "tests/integration/test_end_to_end_workflow.py::test_workflow_records_latency_and_termination_reason"

Files:
  - src/lead_sla_agent/intake/lead_service.py
  - src/lead_sla_agent/conversation/loop.py
  - src/lead_sla_agent/workers/outbound.py
  - tests/integration/test_end_to_end_workflow.py

Context-Refs:
  - docs/ARCHITECTURE.md#data-flow
  - docs/spec.md#overview

Notes: |
  Use fake provider adapters and seeded retrieval fixtures. Do not require real external credentials for this task.

---

## Phase 6 - Evaluation, Hardening, and Deployment Readiness

Goal: make the pilot measurable, observable, and deployable without over-escalating runtime complexity.

## T16: Active Profile Eval Gates in CI

Owner:      codex
Phase:      6
Type:       rag:query tool:call agent:termination
Depends-On: T10, T12, T13

Objective: |
  Add CI evaluation steps for retrieval, tool-use, and agent loop regression checks, and record baseline metrics in the matching eval artifacts.

Acceptance-Criteria:
  - id: AC-1
    description: "CI runs `tests/eval/test_retrieval_eval.py`, `tests/eval/test_tool_eval.py`, and `tests/eval/test_agent_eval.py` in separate named steps. Verified by tests/unit/test_ci_eval_gates.py::test_ci_runs_active_profile_eval_steps."
    test: "tests/unit/test_ci_eval_gates.py::test_ci_runs_active_profile_eval_steps"
  - id: AC-2
    description: "Each active profile eval artifact contains a baseline row with date, dataset/version, metrics, result, and regression rule. Verified by tests/eval/test_eval_artifacts.py::test_active_eval_artifacts_have_baseline_rows."
    test: "tests/eval/test_eval_artifacts.py::test_active_eval_artifacts_have_baseline_rows"
  - id: AC-3
    description: "A simulated retrieval no-answer regression causes the retrieval eval test to fail. Verified by tests/eval/test_eval_artifacts.py::test_retrieval_no_answer_regression_fails_eval."
    test: "tests/eval/test_eval_artifacts.py::test_retrieval_no_answer_regression_fails_eval"

Files:
  - .github/workflows/ci.yml
  - tests/unit/test_ci_eval_gates.py
  - tests/eval/test_eval_artifacts.py
  - docs/retrieval_eval.md
  - docs/tool_eval.md
  - docs/agent_eval.md
  - docs/EVIDENCE_INDEX.md

Context-Refs:
  - docs/IMPLEMENTATION_CONTRACT.md#profile-evaluation-rules
  - docs/CODEX_PROMPT.md#evaluation-state

Notes: |
  This task makes evals part of the merge gate for active profiles.

Execution-Mode: heavy
Evidence:
  - .github/workflows/ci.yml active eval steps
  - tests/eval/test_eval_artifacts.py
  - docs/retrieval_eval.md, docs/tool_eval.md, docs/agent_eval.md baseline rows
Verifier-Focus: |
  Confirm CI can fail on a profile regression even when unit tests are otherwise green.

## T17: Metrics, Health, and NFR Baseline

Owner:      codex
Phase:      6
Type:       none
Depends-On: T15

Objective: |
  Add metrics for first-response latency, SLA breach rate, provider send failure rate, retrieval latency, insufficient-evidence rate, tool-call success, and agent termination reasons, then initialize the NFR baseline.

Acceptance-Criteria:
  - id: AC-1
    description: "Processing an inbound event emits metrics for first-response latency, SLA status, retrieval latency when retrieval runs, tool-call result, and termination reason. Verified by tests/integration/test_metrics.py::test_workflow_emits_required_metrics."
    test: "tests/integration/test_metrics.py::test_workflow_emits_required_metrics"
  - id: AC-2
    description: "`GET /health` includes database, Redis, and retrieval freshness status without lead PII. Verified by tests/integration/test_health.py::test_health_reports_dependencies_without_pii."
    test: "tests/integration/test_health.py::test_health_reports_dependencies_without_pii"
  - id: AC-3
    description: "`docs/nfr.md` records initial targets for first-response p95, deterministic acknowledgement latency, retrieval p95, and provider send failure rate. Verified by tests/unit/test_nfr_doc.py::test_nfr_doc_contains_required_targets."
    test: "tests/unit/test_nfr_doc.py::test_nfr_doc_contains_required_targets"

Files:
  - src/lead_sla_agent/observability/metrics.py
  - src/lead_sla_agent/api/health.py
  - tests/integration/test_metrics.py
  - tests/integration/test_health.py
  - tests/unit/test_nfr_doc.py
  - docs/nfr.md

Context-Refs:
  - docs/ARCHITECTURE.md#observability

Notes: |
  NFR targets are pilot baselines, not scaled production commitments.

## T18: Deployment and Operator Runbook

Owner:      codex
Phase:      6
Type:       none
Depends-On: T16, T17

Objective: |
  Add Docker Compose deployment files, environment documentation, seed-data instructions, backup/rollback notes, and an operator runbook for the first pilot.

Acceptance-Criteria:
  - id: AC-1
    description: "`docker compose config` validates API, worker, PostgreSQL, and Redis services with required environment variables declared. Verified by tests/unit/test_deployment_docs.py::test_docker_compose_config_declares_required_services."
    test: "tests/unit/test_deployment_docs.py::test_docker_compose_config_declares_required_services"
  - id: AC-2
    description: "`docs/runbook.md` lists setup, webhook configuration, seed knowledge ingestion, operator review, rollback, and safe handoff procedures. Verified by tests/unit/test_deployment_docs.py::test_runbook_contains_required_sections."
    test: "tests/unit/test_deployment_docs.py::test_runbook_contains_required_sections"
  - id: AC-3
    description: "`docs/runbook.md` states that real provider tokens must come from environment or deployment secrets and must not be committed. Verified by tests/unit/test_deployment_docs.py::test_runbook_documents_secret_source."
    test: "tests/unit/test_deployment_docs.py::test_runbook_documents_secret_source"

Files:
  - Dockerfile
  - compose.yml
  - docs/runbook.md
  - tests/unit/test_deployment_docs.py

Context-Refs:
  - docs/ARCHITECTURE.md#runtime-and-isolation-model
  - docs/IMPLEMENTATION_CONTRACT.md#credentials-and-secrets

Notes: |
  Keep deployment at T1. Any T2/T3 runtime change requires ADR before implementation.
