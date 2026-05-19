# Tasks - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Status: Active development loop backlog

This document is the active task graph for the next development loop. It starts after the completed T01-T18 prototype graph, which is archived at `docs/archive/tasks_T01_T18_completed.md`.

The goal is to turn the validated prototype into a mature production-ready product. The backlog is intentionally market-aware: technical maturity is not complete unless it improves pilot reliability, operator trust, and measurable lead-conversion value.

Use this document with `docs/CODEX_PROMPT.md` and `docs/prompts/LOOP_TASK_PROMPT.md`. The loop implements one `Next Task` at a time, keeps prompts small, and records details in evidence artifacts instead of expanding prompt files.

---

## Execution Rules

- Preserve the immutable rules in `docs/IMPLEMENTATION_CONTRACT.md`.
- Keep runtime at T1 unless an ADR explicitly approves a runtime-tier change.
- Active profile eval artifacts remain mandatory: `docs/retrieval_eval.md`, `docs/tool_eval.md`, and `docs/agent_eval.md`.
- A task is not production-ready if it only passes unit tests but does not produce evidence in tests, eval artifacts, runbooks, or pilot metrics.
- Every phase has two gates:
  - **Engineering gate:** tests, lint, evals, security boundaries, and rollback evidence pass.
  - **Market gate:** the work improves a concrete pilot metric, buyer proof point, or onboarding/sales readiness.

---

## Phase 7 - Production Persistence and Runtime Hardening

Goal: replace in-memory/fake runtime paths with durable PostgreSQL/Redis behavior while preserving tenant isolation, idempotency, auditability, and restart safety.

### T19: Database-Backed Lead, Conversation, Transcript, Review, and Outcome Repositories

Owner: codex
Phase: 7
Type: persistence tenant:safety
Depends-On: T18

Objective: |
  Replace in-memory repositories used in runtime paths with async SQLAlchemy repositories for leads, conversations, transcripts, review tasks, approvals, and outcome labels.

Acceptance-Criteria:
  - AC-1: Lead, conversation, transcript, review task, approval, and outcome label writes persist to PostgreSQL and survive app restart. Verified by integration tests using PostgreSQL service.
  - AC-2: Every tenant-scoped repository call requires tenant ID and applies transaction-scoped tenant context before query execution.
  - AC-3: Cross-tenant reads for leads, transcripts, review tasks, and outcomes return no rows.
  - AC-4: No raw PII appears in repository exceptions, logs, spans, metrics, or snapshots.

Files:
  - `src/lead_sla_agent/db/lead_repository.py`
  - `src/lead_sla_agent/db/transcript_repository.py`
  - `src/lead_sla_agent/operator/review_queue.py`
  - `src/lead_sla_agent/operator/outcomes.py`
  - `tests/integration/test_persistent_repositories.py`

Evidence:
  - PostgreSQL-backed integration tests.
  - Tenant isolation tests.
  - SQL safety tests.

Market-Gate:
  - Pilot operator can reload the system and still see all leads, transcripts, reviews, and outcomes.

### T20: Transactional Intake and Idempotent Event Processing

Owner: codex
Phase: 7
Type: persistence intake idempotency
Depends-On: T19

Objective: |
  Make signed webhook intake transactional: provider event, lead, conversation, initial transcript, and audit event are committed atomically and replay-safe.

Acceptance-Criteria:
  - AC-1: Replayed source event IDs return the existing provider event and do not create duplicate leads or messages.
  - AC-2: Failed transcript or audit write rolls back the whole intake transaction.
  - AC-3: Payload hash and source event ID are stored without raw webhook payload persistence.
  - AC-4: Intake latency is measured and recorded.

Files:
  - `src/lead_sla_agent/api/webhooks.py`
  - `src/lead_sla_agent/intake/lead_service.py`
  - `src/lead_sla_agent/db/repositories.py`
  - `tests/integration/test_transactional_intake.py`

Evidence:
  - Transaction rollback tests.
  - Replay/idempotency tests.
  - Metrics assertions.

Market-Gate:
  - Duplicate provider delivery cannot inflate lead counts or operator workload.

### T21: Redis-Backed SLA Timers and Provider Retry Workers

Owner: codex
Phase: 7
Type: queue runtime
Depends-On: T20

Objective: |
  Replace deterministic in-memory SLA/retry helpers with Redis-backed async queue workers for first-response timers, outbound retry, and provider-error fallback.

Acceptance-Criteria:
  - AC-1: SLA timer job marks `sla_breached_at` exactly once when no outbound send is confirmed before threshold.
  - AC-2: Retry worker retries provider sends up to configured limit and then creates a human-review task.
  - AC-3: Redis access uses only `redis.asyncio`.
  - AC-4: Worker jobs are idempotent under duplicate delivery.

Files:
  - `src/lead_sla_agent/workers/queue.py`
  - `src/lead_sla_agent/workers/sla.py`
  - `src/lead_sla_agent/workers/retries.py`
  - `tests/integration/test_redis_workers.py`

Evidence:
  - Redis integration tests.
  - Duplicate delivery tests.
  - Retry exhaustion tests.

Market-Gate:
  - The system reliably flags missed-response risk without manual monitoring.

### T22: Row-Level Security and Tenant Isolation Drill

Owner: codex
Phase: 7
Type: security tenant:safety
Depends-On: T19

Objective: |
  Add PostgreSQL RLS policies for tenant-scoped tables and prove app/database isolation even if an application query is wrong.

Acceptance-Criteria:
  - AC-1: RLS policies exist for every tenant-scoped table.
  - AC-2: Direct cross-tenant SQL queries return no rows when tenant context is set.
  - AC-3: Missing tenant context fails closed.
  - AC-4: Migration tests verify RLS remains enabled.

Files:
  - `alembic/versions/*_rls_policies.py`
  - `src/lead_sla_agent/db/tenant.py`
  - `tests/integration/test_rls_tenant_isolation.py`

Evidence:
  - RLS integration tests.
  - Migration metadata checks.

Market-Gate:
  - Multi-tenant pilot can be sold without cross-customer data exposure risk.

### T23: Backup, Restore, and Migration Drill

Owner: codex
Phase: 7
Type: ops reliability
Depends-On: T22

Objective: |
  Add documented backup/restore procedures and testable migration safety checks for the pilot deployment.

Acceptance-Criteria:
  - AC-1: Runbook documents backup schedule, restore command, and restore verification checklist.
  - AC-2: A local restore drill can load a fixture dump and pass core smoke tests.
  - AC-3: Forward migrations have rollback notes or explicit irreversible rationale.

Files:
  - `docs/runbook.md`
  - `scripts/backup_postgres.sh`
  - `scripts/restore_postgres.sh`
  - `tests/unit/test_runbook_backup_restore.py`

Evidence:
  - Runbook test.
  - Restore drill notes.

Market-Gate:
  - A pilot customer can be told how data recovery works in plain language.

---

## Phase 8 - Real Provider Integrations

Goal: connect one real messaging channel, one calendar provider, and one CRM/spreadsheet destination without weakening safety or requiring live credentials in normal tests.

### T24: First Real Messaging Provider Adapter

Owner: codex
Phase: 8
Type: tool:call provider
Depends-On: T21

Objective: |
  Implement the first production messaging adapter, preferably the channel chosen for the pilot vertical.

Acceptance-Criteria:
  - AC-1: Adapter reads only provider-specific environment variables.
  - AC-2: Unit and integration tests use fake provider responses and do not require live credentials.
  - AC-3: Sends use idempotency key and record provider message ID, status, latency, and failure reason.
  - AC-4: Unsafe message categories still route to human review before provider execution.

Files:
  - `src/lead_sla_agent/tools/messaging.py`
  - `src/lead_sla_agent/config.py`
  - `tests/integration/test_messaging_provider.py`
  - `docs/tool_eval.md`

Evidence:
  - Fake-provider tests.
  - Tool eval update.
  - Secret-scope test.

Market-Gate:
  - Pilot can send/receive through the channel the buyer already uses.

### T25: Calendar Lookup and Booking Provider Adapter

Owner: codex
Phase: 8
Type: tool:call booking
Depends-On: T24

Objective: |
  Implement a real calendar provider adapter with fresh-slot lookup, explicit customer acceptance, booking idempotency, and fallback to human review.

Acceptance-Criteria:
  - AC-1: Booking without fresh lookup is rejected.
  - AC-2: Booking without explicit customer acceptance is rejected.
  - AC-3: Duplicate booking idempotency key returns existing booking mapping.
  - AC-4: Provider timeout creates retry or human-review fallback according to policy.

Files:
  - `src/lead_sla_agent/tools/calendar.py`
  - `tests/integration/test_calendar_provider.py`
  - `docs/tool_eval.md`

Evidence:
  - Freshness tests.
  - Idempotency tests.
  - Timeout fallback tests.

Market-Gate:
  - The workflow can turn qualified leads into real booked appointments.

### T26: CRM or Spreadsheet Destination Adapter

Owner: codex
Phase: 8
Type: tool:call crm
Depends-On: T24

Objective: |
  Implement the first lead record destination, selected for the pilot buyer's current workflow.

Acceptance-Criteria:
  - AC-1: Create/update writes are idempotent by source event ID or lead ID.
  - AC-2: Duplicate writes return existing remote mapping.
  - AC-3: Provider credentials are adapter-scoped.
  - AC-4: Failed CRM write does not block safe customer acknowledgement; it creates an audit event and retry/handoff path.

Files:
  - `src/lead_sla_agent/tools/crm.py`
  - `tests/integration/test_crm_provider.py`
  - `docs/tool_eval.md`

Evidence:
  - Fake-provider tests.
  - Idempotency evidence.

Market-Gate:
  - Customer's existing team can see AI-captured leads where they already work.

### T27: Provider Webhook Verification Matrix

Owner: codex
Phase: 8
Type: intake provider security
Depends-On: T24

Objective: |
  Add provider-specific webhook signature verification and event normalization for each enabled inbound channel.

Acceptance-Criteria:
  - AC-1: Each provider has an explicit signature verifier.
  - AC-2: Invalid signature writes no provider, lead, conversation, message, or audit rows.
  - AC-3: Provider-specific user/message IDs are treated as PII in observability.
  - AC-4: Normalized events preserve source event ID, channel, tenant, received timestamp, and payload hash.

Files:
  - `src/lead_sla_agent/intake/signatures.py`
  - `src/lead_sla_agent/intake/normalizer.py`
  - `tests/integration/test_provider_webhooks.py`

Evidence:
  - Per-provider signature tests.
  - PII scrubber tests.

Market-Gate:
  - Buyer can connect real inbound sources without custom engineering each time.

---

## Phase 9 - LLM and Retrieval Productionization

Goal: make AI behavior reliable, measurable, grounded, and maintainable on a real pilot corpus.

### T28: Production Embedding Adapter Selection

Owner: codex
Phase: 9
Type: rag:ingestion model
Depends-On: T24

Objective: |
  Select and implement a real text embedding provider behind the existing embedding adapter contract.

Acceptance-Criteria:
  - AC-1: Embedding model, dimensions, index schema version, and reindex requirement are recorded.
  - AC-2: Unit tests use fake embeddings; live provider tests are opt-in.
  - AC-3: Changing model or dimensions requires ADR and reindex plan.
  - AC-4: `docs/retrieval_eval.md` compares deterministic baseline to production embedding baseline.

Files:
  - `src/lead_sla_agent/retrieval/embeddings.py`
  - `docs/adr/*embedding*.md`
  - `docs/retrieval_eval.md`
  - `tests/integration/test_embedding_adapter.py`

Evidence:
  - ADR.
  - Retrieval eval row.
  - Adapter tests.

Market-Gate:
  - Retrieval works on real business language, not only synthetic fixtures.

### T29: Tenant Knowledge Admin API

Owner: codex
Phase: 9
Type: rag:ingestion operator
Depends-On: T28

Objective: |
  Add an authenticated API for uploading, listing, disabling, and reindexing tenant-approved knowledge documents.

Acceptance-Criteria:
  - AC-1: Operators can upload markdown/text/CSV-like policy sources.
  - AC-2: Disabled documents are not retrieved.
  - AC-3: Reindex action records actor, timestamp, corpus version, and index schema version.
  - AC-4: Uploads reject raw customer transcript data unless explicitly marked as approved knowledge.

Files:
  - `src/lead_sla_agent/operator/knowledge_api.py`
  - `src/lead_sla_agent/retrieval/ingestion.py`
  - `tests/integration/test_knowledge_admin.py`

Evidence:
  - Auth tests.
  - Corpus version tests.
  - Retrieval eval update.

Market-Gate:
  - Non-engineer operator can keep the AI knowledge current.

### T30: Retrieval Eval Dataset Expansion from Pilot Questions

Owner: codex
Phase: 9
Type: rag:query eval
Depends-On: T29

Objective: |
  Expand retrieval evals from synthetic seed cases to real pilot questions collected from transcripts and operator feedback.

Acceptance-Criteria:
  - AC-1: Dataset has at least 50 questions from pilot-like scenarios.
  - AC-2: Dataset includes pricing, service area, cancellation, booking, exact terms, unsupported, stale, and tenant isolation slices.
  - AC-3: Eval rows include Date, Eval Source, Corpus version, Dataset, Metrics, Root cause, Result, and Notes.
  - AC-4: No raw customer PII is stored in eval fixtures.

Files:
  - `tests/eval/fixtures/retrieval_pilot_seed.json`
  - `docs/retrieval_eval.md`
  - `tests/eval/test_retrieval_eval.py`

Evidence:
  - Eval tests.
  - PII fixture scan.

Market-Gate:
  - Retrieval quality reflects real buyer questions.

### T31: Prompt, Model, and Policy Version Tracking

Owner: codex
Phase: 9
Type: agent:loop model governance
Depends-On: T30

Objective: |
  Version all prompt/policy/model contracts used for extraction, reply drafting, handoff summaries, and safety decisions.

Acceptance-Criteria:
  - AC-1: Every model output stores model name, prompt version, schema version, and policy decision.
  - AC-2: Prompt changes require eval comparison before rollout.
  - AC-3: Unsupported evidence cannot produce customer-facing text.
  - AC-4: Eval artifacts identify prompt/model versions.

Files:
  - `src/lead_sla_agent/conversation/model_io.py`
  - `src/lead_sla_agent/conversation/policy.py`
  - `docs/agent_eval.md`
  - `tests/integration/test_model_versioning.py`

Evidence:
  - Agent eval update.
  - Model version tests.

Market-Gate:
  - Buyer-facing behavior can be explained and rolled back.

---

## Phase 10 - Operator Productization

Goal: make human-in-the-loop review fast, auditable, and useful for improving the system.

### T32: Operator Dashboard or Production Console

Owner: codex
Phase: 10
Type: operator ux
Depends-On: T14

Objective: |
  Build the first operator surface for review queue, transcript inspection, evidence inspection, approve/edit/send, and outcome labels.

Acceptance-Criteria:
  - AC-1: Operator can inspect lead summary, transcript refs, evidence IDs, proposed reply, and required action.
  - AC-2: Operator can approve, edit, send, or mark as no-send.
  - AC-3: Every action records actor ID, timestamp, hashes, reason code, and final status.
  - AC-4: Unauthorized users cannot access operator data.

Files:
  - `src/lead_sla_agent/operator/api.py`
  - frontend or internal console path selected by ADR
  - `tests/integration/test_operator_dashboard.py`

Evidence:
  - Operator workflow tests.
  - Auth/RBAC tests.

Market-Gate:
  - Human reviewers can clear edge cases faster than manual inbox handling.

### T33: Feedback Loop from Operator Outcomes to Eval Fixtures

Owner: codex
Phase: 10
Type: eval operator
Depends-On: T32

Objective: |
  Convert approved/rejected operator decisions into labeled eval candidates for retrieval, tool, and agent regressions.

Acceptance-Criteria:
  - AC-1: Operator feedback exports de-identified candidate eval rows.
  - AC-2: Human approval is required before adding feedback to canonical eval datasets.
  - AC-3: Regression tests can run against accepted feedback fixtures.

Files:
  - `src/lead_sla_agent/operator/feedback.py`
  - `tests/eval/fixtures/operator_feedback_candidates.json`
  - `docs/agent_eval.md`
  - `docs/retrieval_eval.md`

Evidence:
  - Feedback export tests.
  - PII scan.

Market-Gate:
  - The product improves from real operator corrections.

---

## Phase 11 - Pilot Vertical Package

Goal: stop selling a generic AI agent and package one vertical-specific offer with measurable ROI.

### T34: Select First Pilot Vertical and Buyer Persona

Owner: human + codex
Phase: 11
Type: market strategy
Depends-On: T30

Objective: |
  Pick one time-sensitive service vertical and define the first buyer persona, lead sources, response pain, and measurable value hypothesis.

Acceptance-Criteria:
  - AC-1: Document selected vertical, rejected alternatives, buyer persona, and current workaround.
  - AC-2: Define baseline metrics: median response time, missed lead rate, booking rate, and manual review cost.
  - AC-3: Define first 10 target accounts and outreach channel.

Files:
  - `docs/market/pilot_vertical.md`
  - `docs/market/first_10_targets.md`

Evidence:
  - Interview notes or public research links.
  - Buyer pain hypothesis.

Market-Gate:
  - At least 5 target buyers confirm the lead-response pain is real and urgent.

### T35: Vertical Policy Pack

Owner: codex
Phase: 11
Type: product vertical
Depends-On: T34

Objective: |
  Create a reusable vertical configuration pack: required lead fields, approved FAQ schema, unsafe categories, handoff reasons, and operator scripts.

Acceptance-Criteria:
  - AC-1: Vertical pack defines required fields and qualification questions.
  - AC-2: Unsafe/handoff policy covers pricing, commitments, regulated advice, complaints, high-value leads, and booking uncertainty.
  - AC-3: Seed corpus and eval dataset are included.
  - AC-4: Pack can initialize a demo tenant.

Files:
  - `docs/verticals/<vertical>.md`
  - `seed/verticals/<vertical>/`
  - `tests/integration/test_vertical_pack.py`

Evidence:
  - Demo tenant setup test.
  - Eval fixture coverage.

Market-Gate:
  - Demo speaks the buyer's language without custom engineering.

### T36: Pilot ROI Dashboard

Owner: codex
Phase: 11
Type: analytics market
Depends-On: T35

Objective: |
  Add a basic dashboard/API that reports response time, AI-assisted responses, handoff rate, booked outcomes, and before/after comparison.

Acceptance-Criteria:
  - AC-1: Dashboard/API reports first-response latency p50/p95.
  - AC-2: Reports automation success, human-review rate, booked labels, and provider send failures.
  - AC-3: Metrics can be exported for a pilot weekly report.

Files:
  - `src/lead_sla_agent/operator/analytics.py`
  - `tests/integration/test_pilot_analytics.py`
  - `docs/nfr.md`

Evidence:
  - Analytics tests.
  - Sample weekly report.

Market-Gate:
  - Buyer can see whether the product creates booked-call or qualified-handoff lift.

---

## Phase 12 - Security, Reliability, and Compliance Baseline

Goal: make the pilot safe enough for real customer data without over-claiming formal compliance.

### T37: Production Auth and RBAC

Owner: codex
Phase: 12
Type: security auth
Depends-On: T32

Objective: |
  Replace test bearer auth with production authentication and tenant/role authorization.

Acceptance-Criteria:
  - AC-1: Operator routes require authenticated principal.
  - AC-2: Tenant and role checks happen before data access.
  - AC-3: Auth failures expose no lead, transcript, provider, or tenant data.
  - AC-4: Tests cover owner, operator, viewer, and unauthorized roles.

Files:
  - `src/lead_sla_agent/operator/auth.py`
  - `tests/integration/test_operator_auth_rbac.py`

Evidence:
  - RBAC tests.
  - Security review notes.

Market-Gate:
  - Customer can safely give multiple team members access.

### T38: Secrets Management and Environment Partitioning

Owner: codex
Phase: 12
Type: security ops
Depends-On: T24

Objective: |
  Document and enforce separate local, staging, and production secrets with adapter-scoped access.

Acceptance-Criteria:
  - AC-1: Runbook describes secret source for every provider.
  - AC-2: Tests reject real-looking credentials in fixtures and docs.
  - AC-3: API and worker receive only required variables.
  - AC-4: Rotation procedure is documented.

Files:
  - `docs/runbook.md`
  - `compose.yml`
  - `tests/unit/test_secret_policy.py`

Evidence:
  - Secret scan tests.
  - Runbook section.

Market-Gate:
  - Deployment can be operated without credential leaks.

### T39: Data Retention, Export, and Delete Procedures

Owner: codex
Phase: 12
Type: privacy ops
Depends-On: T19

Objective: |
  Add tenant-level data export and deletion procedures aligned with pilot privacy expectations.

Acceptance-Criteria:
  - AC-1: Tenant export includes leads, conversations, transcripts, audit, outcomes, and review tasks.
  - AC-2: Delete/anonymize operation is documented with audit record.
  - AC-3: Retention policy is configurable per tenant.
  - AC-4: PII fields are identified in export schema.

Files:
  - `src/lead_sla_agent/operator/data_admin.py`
  - `docs/runbook.md`
  - `tests/integration/test_data_export_delete.py`

Evidence:
  - Export/delete tests.
  - Privacy runbook.

Market-Gate:
  - Buyer can answer "what happens to customer data?" clearly.

### T40: Production Observability and Incident Runbook

Owner: codex
Phase: 12
Type: observability ops
Depends-On: T17

Objective: |
  Add dashboards/alerts for latency, send failures, SLA breaches, retrieval freshness, insufficient evidence, tool failures, and queue depth.

Acceptance-Criteria:
  - AC-1: Metrics have stable names and documented labels without PII.
  - AC-2: Alert thresholds are documented.
  - AC-3: Incident runbook covers provider outage, retrieval regression, queue backlog, and webhook signature failures.
  - AC-4: Health endpoint remains PII-free.

Files:
  - `docs/runbook.md`
  - `docs/nfr.md`
  - `src/lead_sla_agent/observability/metrics.py`
  - `tests/unit/test_observability_contract.py`

Evidence:
  - Metrics contract tests.
  - Incident runbook.

Market-Gate:
  - Operator can detect and explain service failures during pilot.

---

## Phase 13 - Revenue Validation

Goal: prove the product creates economic value before scaling the platform.

### T41: Pilot Measurement Plan

Owner: human + codex
Phase: 13
Type: market analytics
Depends-On: T36

Objective: |
  Define the before/after measurement plan for the first pilot.

Acceptance-Criteria:
  - AC-1: Baseline period and pilot period are defined.
  - AC-2: Metrics include response time, lead capture, booked calls, qualified handoffs, review rate, and cost per lead.
  - AC-3: Report template exists for weekly buyer update.

Files:
  - `docs/market/pilot_measurement_plan.md`
  - `docs/market/weekly_report_template.md`

Evidence:
  - Measurement plan.
  - Sample report.

Market-Gate:
  - Buyer agrees the metrics would justify payment or expansion.

### T42: Pricing and Packaging Experiment

Owner: human + codex
Phase: 13
Type: market pricing
Depends-On: T41

Objective: |
  Define and test pricing around saved leads/booked appointments rather than generic AI usage.

Acceptance-Criteria:
  - AC-1: At least two pricing hypotheses are documented.
  - AC-2: Pricing aligns with lead value and review workload.
  - AC-3: Pilot contract terms and success criteria are drafted.

Files:
  - `docs/market/pricing.md`
  - `docs/market/pilot_terms.md`

Evidence:
  - Buyer feedback.
  - Pricing decision log.

Market-Gate:
  - At least one buyer accepts pilot terms or gives a clear objection to address.

### T43: Case Study and Sales Proof Kit

Owner: human + codex
Phase: 13
Type: market sales
Depends-On: T41

Objective: |
  Produce the first buyer-facing proof kit from pilot metrics and operator feedback.

Acceptance-Criteria:
  - AC-1: Case study template includes baseline, intervention, measurable result, and quote slot.
  - AC-2: Demo script maps to selected vertical pain.
  - AC-3: Objection handling doc covers safety, data, integration, and pricing.

Files:
  - `docs/market/case_study_template.md`
  - `docs/market/demo_script.md`
  - `docs/market/objections.md`

Evidence:
  - Sales proof kit.

Market-Gate:
  - Sales conversation can focus on missed-revenue recovery, not AI novelty.

---

## Phase 14 - Sales-Ready MVP

Goal: make onboarding repeatable for the next 5-10 customers.

### T44: Assisted Onboarding Workflow

Owner: codex
Phase: 14
Type: product onboarding
Depends-On: T35

Objective: |
  Build a guided setup flow or checklist for tenant creation, provider connection, knowledge upload, operator accounts, and test lead validation.

Acceptance-Criteria:
  - AC-1: Onboarding checklist can initialize a new tenant in under one working day.
  - AC-2: Provider connection test sends/receives a fake or sandbox event.
  - AC-3: Knowledge ingestion test verifies at least 10 tenant questions.
  - AC-4: Operator approval path is tested before launch.

Files:
  - `docs/runbook.md`
  - `scripts/onboard_tenant.py`
  - `tests/integration/test_onboarding_flow.py`

Evidence:
  - Onboarding test.
  - Tenant launch checklist.

Market-Gate:
  - Founder/operator can onboard a second customer without bespoke engineering.

### T45: Demo Tenant and Sales Sandbox

Owner: codex
Phase: 14
Type: demo sales
Depends-On: T44

Objective: |
  Create a safe demo tenant with seed leads, corpus, review tasks, and analytics for sales calls.

Acceptance-Criteria:
  - AC-1: Demo tenant contains no real customer PII.
  - AC-2: Demo shows supported FAQ, unsupported handoff, booking proposal, and operator approval.
  - AC-3: Demo reset command restores known state.

Files:
  - `seed/demo_tenant/`
  - `scripts/reset_demo_tenant.py`
  - `tests/integration/test_demo_tenant.py`

Evidence:
  - Demo reset tests.
  - PII scan.

Market-Gate:
  - Sales demo can be run repeatedly without engineering support.

### T46: Support and Operations Process

Owner: human + codex
Phase: 14
Type: ops support
Depends-On: T44

Objective: |
  Define support process for pilot customers: issue intake, severity, response SLA, escalation, and post-incident review.

Acceptance-Criteria:
  - AC-1: Support runbook defines severity levels and response expectations.
  - AC-2: Incident template exists.
  - AC-3: Customer communication templates exist for provider outage and AI safety handoff.

Files:
  - `docs/support/runbook.md`
  - `docs/support/incident_template.md`
  - `docs/support/customer_templates.md`

Evidence:
  - Support docs.

Market-Gate:
  - Pilot customer knows how issues are handled.

---

## Phase 15 - Multi-Tenant SaaS Scale

Goal: scale only after pilot value is proven.

### T47: Tenant Admin and Configuration

Owner: codex
Phase: 15
Type: saas tenant
Depends-On: T44

Objective: |
  Add tenant admin configuration for channels, business hours, required fields, max turns, handoff policy, and provider settings.

Acceptance-Criteria:
  - AC-1: Tenant admin can update safe configuration without code deployment.
  - AC-2: Dangerous policy changes require elevated role or approval.
  - AC-3: Config changes are audited and versioned.

Files:
  - `src/lead_sla_agent/operator/tenant_admin.py`
  - `tests/integration/test_tenant_admin.py`

Evidence:
  - Config tests.
  - Audit tests.

Market-Gate:
  - Multiple customers can run with different policies.

### T48: Usage Metering and Billing Readiness

Owner: codex
Phase: 15
Type: billing analytics
Depends-On: T36

Objective: |
  Track usage dimensions needed for pricing: leads processed, AI-assisted replies, provider sends, review tasks, bookings, and active channels.

Acceptance-Criteria:
  - AC-1: Usage events are tenant-scoped and append-only.
  - AC-2: Monthly usage export exists.
  - AC-3: Billing metrics exclude PII.
  - AC-4: Pricing experiments can map to usage exports.

Files:
  - `src/lead_sla_agent/billing/usage.py`
  - `tests/integration/test_usage_metering.py`

Evidence:
  - Usage export tests.

Market-Gate:
  - Product can support paid pilots and early SaaS billing.

### T49: Staging/Production Release Discipline

Owner: codex
Phase: 15
Type: ops release
Depends-On: T40

Objective: |
  Establish staging/prod separation, migration policy, CI/CD gates, release notes, and rollback validation.

Acceptance-Criteria:
  - AC-1: CI distinguishes unit, integration, eval, and deployment checks.
  - AC-2: Staging deploy runs migrations and smoke tests before production.
  - AC-3: Release notes include model/prompt/schema/eval changes.
  - AC-4: Rollback procedure is tested before production promotion.

Files:
  - `.github/workflows/ci.yml`
  - `.github/workflows/deploy.yml`
  - `docs/runbook.md`
  - `docs/release_template.md`

Evidence:
  - CI/CD config tests.
  - Release checklist.

Market-Gate:
  - Customers can receive reliable updates without surprise regressions.

---

## Recommended Sequence

The highest-leverage path is:

1. Phase 7: durable runtime and tenant safety.
2. Phase 8: one real messaging channel, one real calendar, one real CRM/spreadsheet.
3. Phase 11: one vertical package and first buyer proof.
4. Phase 9 and Phase 10 in parallel: production AI quality plus operator UX.
5. Phase 12 before handling broader customer data.
6. Phase 13 before scaling engineering scope.
7. Phase 14 and Phase 15 only after pilot proof exists.

Avoid building generic SaaS scale before one vertical has a credible booked-lead or qualified-handoff lift.
