# Tasks - Lead Response SLA Agent

Version: 1.2
Last updated: 2026-05-29
Status: Paused/reference product backlog

This document is the active task graph for the next development loop. It starts after the completed T01-T18 prototype graph, which is archived at `docs/archive/tasks_T01_T18_completed.md`.

The original goal was to turn the validated prototype into a mature
production-ready product. As of the 2026-05-29 portfolio review, the project is
paused as a standalone product unless real business usage or pilot data appears.
Its current value is as a reference implementation for safe tool use,
human-in-the-loop messaging, tenant isolation, and eval-driven agent workflows.

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

Current pause rule:

- Do not implement new provider, persistence, or production hardening work unless
  a real pilot/business need supplies data and a human explicitly reactivates
  the product.
- Reusable patterns should be extracted into Workflow-To-Agent Studio,
  AI Rollout Training OS, or AI Workflow Playbook instead of expanding this app.

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

## Phase 16 - Production Data Durability

Goal: replace remaining in-memory/admin-grade contracts with durable, queryable, tenant-safe production storage.

### T50: Persistent Tenant Configuration Store

Owner: codex
Phase: 16
Type: persistence tenant:safety admin
Depends-On: T47

Objective: |
  Replace the in-memory tenant admin store with PostgreSQL-backed versioned configuration storage for channels, business hours, required fields, max turns, handoff policy, autonomous-send policy, and provider settings.

Acceptance-Criteria:
  - AC-1: Tenant config survives process restart and is loaded by tenant ID only.
  - AC-2: Every config mutation creates a new version and immutable audit record.
  - AC-3: Dangerous fields still require owner role or approval ID.
  - AC-4: Concurrent updates use optimistic locking or equivalent version conflict detection.
  - AC-5: Cross-tenant reads and updates are denied by repository checks and PostgreSQL RLS.

Files:
  - `src/lead_sla_agent/operator/tenant_admin.py`
  - `src/lead_sla_agent/db/tenant_config_repository.py`
  - `alembic/versions/*_tenant_config.py`
  - `tests/integration/test_tenant_admin_persistence.py`

Evidence:
  - PostgreSQL persistence tests.
  - RLS isolation tests.
  - Restart/reload test.

Market-Gate:
  - Customer policy changes can be made safely without code deploys or data loss.

### T51: Persistent Usage and Billing Event Ledger

Owner: codex
Phase: 16
Type: billing persistence privacy
Depends-On: T48

Objective: |
  Replace in-memory usage metering with an append-only PostgreSQL ledger that supports monthly exports, pricing experiments, and future billing reconciliation.

Acceptance-Criteria:
  - AC-1: Usage events are append-only and tenant-scoped.
  - AC-2: Duplicate event IDs are idempotent and do not inflate billing totals.
  - AC-3: Monthly exports can be regenerated deterministically from the ledger.
  - AC-4: Exported usage contains no raw PII and rejects unsupported metadata.
  - AC-5: Pricing package mapping is versioned so historical invoices remain explainable.

Files:
  - `src/lead_sla_agent/billing/usage.py`
  - `src/lead_sla_agent/db/usage_repository.py`
  - `alembic/versions/*_usage_ledger.py`
  - `tests/integration/test_usage_metering_persistence.py`

Evidence:
  - Ledger append-only tests.
  - Idempotency tests.
  - Monthly export snapshot tests with PII scan.

Market-Gate:
  - Paid pilots can be invoiced from auditable, reproducible usage data.

### T52: Immutable Audit Event Store

Owner: codex
Phase: 16
Type: audit compliance tenant:safety
Depends-On: T50

Objective: |
  Centralize tenant-scoped audit events for approvals, config changes, provider sends, data export/delete, billing exports, and release-impacting operator actions.

Acceptance-Criteria:
  - AC-1: Audit events are append-only and include tenant ID, actor hash/ref, action, resource type, resource ID/ref, result, policy version, and timestamp.
  - AC-2: Audit event payloads reject raw PII and secrets.
  - AC-3: Audit search is tenant-scoped and role-gated.
  - AC-4: Existing review, approval, data admin, tenant admin, and billing flows emit audit events.
  - AC-5: Retention and export behavior is documented.

Files:
  - `src/lead_sla_agent/audit/events.py`
  - `src/lead_sla_agent/db/audit_repository.py`
  - `alembic/versions/*_audit_events.py`
  - `docs/runbook.md`
  - `tests/integration/test_audit_event_store.py`

Evidence:
  - Audit append-only tests.
  - PII rejection tests.
  - Tenant-scoped search tests.

Market-Gate:
  - Founder/operator can explain who changed what and why during a customer escalation.

---

## Phase 17 - Real Deployment and Environment Hardening

Goal: make staging and production real environments, not just workflow placeholders.

### T53: Deployment Target ADR and Infrastructure Contract

Owner: human + codex
Phase: 17
Type: ops architecture
Depends-On: T49

Objective: |
  Choose the first production hosting target and document the deployment contract for API, worker, PostgreSQL, Redis, migrations, secrets, logs, metrics, backups, and rollback.

Acceptance-Criteria:
  - AC-1: ADR names the chosen platform and rejected alternatives.
  - AC-2: Runtime tier remains T1 unless the ADR explicitly changes it with risk justification.
  - AC-3: Required staging and production resources are listed with owner, backup, retention, and cost expectations.
  - AC-4: Deployment commands and rollback commands are concrete enough to run in CI.

Files:
  - `docs/adr/ADR-004-deployment-target.md`
  - `docs/runbook.md`
  - `.github/workflows/deploy.yml`
  - `tests/unit/test_deployment_target_docs.py`

Evidence:
  - ADR test.
  - Runbook test.
  - Deploy workflow command validation.

Market-Gate:
  - A pilot customer can be assigned to a known staging/prod environment with clear operational ownership.

### T54: Staging and Production Secret Partitioning

Owner: codex
Phase: 17
Type: security ops secrets
Depends-On: T53

Objective: |
  Wire environment-specific configuration and secret expectations for staging and production without committing credentials.

Acceptance-Criteria:
  - AC-1: Required secrets are documented separately for local, staging, and production.
  - AC-2: CI validates secret names and missing-secret failure behavior without printing secret values.
  - AC-3: Provider credentials are scoped per adapter and per environment.
  - AC-4: Rotation procedure exists and includes revocation verification.

Files:
  - `src/lead_sla_agent/config.py`
  - `docs/runbook.md`
  - `.github/workflows/deploy.yml`
  - `tests/unit/test_environment_secret_contract.py`

Evidence:
  - Secret contract tests.
  - Redaction tests.
  - Rotation checklist.

Market-Gate:
  - Production cannot accidentally use demo, local, or staging credentials.

### T55: Deployment Smoke Tests

Owner: codex
Phase: 17
Type: ops testing reliability
Depends-On: T54

Objective: |
  Add post-deploy smoke tests that validate health, migrations, queue connectivity, provider sandbox connectivity, operator auth, and safe handoff behavior.

Acceptance-Criteria:
  - AC-1: Smoke test command can target staging or production by URL/environment.
  - AC-2: Smoke tests do not create real customer sends unless sandbox mode is explicitly enabled.
  - AC-3: Smoke tests validate API health, database migration version, Redis connectivity, operator auth, and provider sandbox path.
  - AC-4: Production deploy workflow requires staging smoke success before production promotion.

Files:
  - `scripts/smoke_test.py`
  - `.github/workflows/deploy.yml`
  - `docs/runbook.md`
  - `tests/integration/test_smoke_tests.py`

Evidence:
  - Smoke test unit/integration tests.
  - Deploy workflow gate test.

Market-Gate:
  - Releases can be promoted only after proving the core lead path still works.

### T56: Rollback Rehearsal and Migration Safety

Owner: codex
Phase: 17
Type: ops rollback database
Depends-On: T55

Objective: |
  Turn rollback from documentation into a rehearsed command path for app rollback, migration rollback, and restore-from-backup decision points.

Acceptance-Criteria:
  - AC-1: Every new migration has downgrade coverage or an explicit irreversible rationale.
  - AC-2: Staging rollback rehearsal records migration version before and after rollback.
  - AC-3: Runbook defines when to rollback app only, rollback migration, or restore backup.
  - AC-4: CI validates rollback rehearsal artifacts exist before production deploy.

Files:
  - `alembic/versions/`
  - `scripts/rollback_check.py`
  - `docs/runbook.md`
  - `.github/workflows/deploy.yml`
  - `tests/unit/test_rollback_rehearsal.py`

Evidence:
  - Rollback command tests.
  - Migration downgrade metadata checks.
  - Staging rehearsal artifact.

Market-Gate:
  - A failed release has a practiced recovery path before customer impact grows.

---

## Phase 18 - Live Provider Production Readiness

Goal: move from fake/sandbox provider contracts to controlled live-provider operation.

### T57: Live Messaging Provider Pilot Path

Owner: human + codex
Phase: 18
Type: provider messaging safety
Depends-On: T24, T55

Objective: |
  Configure the first live messaging provider path for one pilot tenant with human approval enforced before every outbound message.
  The pilot messaging matrix is email via Postmark, WhatsApp via Twilio WhatsApp, and Telegram via the Telegram Bot API.
  T57 implements the common outbound provider contract and first controlled live-send path without requiring real credentials in normal tests.

Acceptance-Criteria:
  - AC-1: Live provider credentials are environment-scoped and never required for normal tests; provider choices are documented as Postmark email, Twilio WhatsApp, and Telegram Bot API.
  - AC-2: Provider send path records provider name, channel, provider message ID, latency, delivery status, failure reason, idempotency key, and rate-limit flag.
  - AC-3: Pilot tenant defaults to human approval for all outbound messages across email, WhatsApp, and Telegram.
  - AC-4: Provider failure creates retry or human-review fallback without duplicate sends.
  - AC-5: Provider rate-limit response is handled and visible in operator/reliability metrics.
  - AC-6: WhatsApp outbound requires explicit opt-in metadata before live send; Telegram outbound requires a known chat ID initiated by the user.

Files:
  - `src/lead_sla_agent/tools/messaging.py`
  - `src/lead_sla_agent/workers/retries.py`
  - `src/lead_sla_agent/config.py`
  - `docs/runbook.md`
  - `tests/integration/test_live_messaging_contract.py`

Evidence:
  - Fake-provider contract tests.
  - Sandbox/live credential checklist.
  - Human-approval gate test.
  - Multi-channel adapter contract tests.

Market-Gate:
  - First pilot can send real replies safely with operator approval.

### T58: Provider Webhook End-to-End Drill

Owner: codex
Phase: 18
Type: provider webhook security
Depends-On: T57

Objective: |
  Prove inbound provider webhooks work end to end through public URL, signature verification, idempotent intake, transcript persistence, and operator review creation for email, WhatsApp, and Telegram.

Acceptance-Criteria:
  - AC-1: Webhook route rejects invalid signatures before persistence for provider-signed channels.
  - AC-2: Replayed provider event IDs are idempotent across Postmark inbound, Twilio WhatsApp, and Telegram updates.
  - AC-3: Public webhook setup is documented for staging and production, including VPS reverse proxy paths.
  - AC-4: Webhook drill creates a lead, transcript entry, and review task without storing raw payload PII.
  - AC-5: Telegram webhook setup records bot token handling without logging token values.
  - AC-6: WhatsApp webhook setup records opt-in/source metadata required for later outbound replies.

Files:
  - `src/lead_sla_agent/api/webhooks.py`
  - `docs/runbook.md`
  - `tests/integration/test_provider_webhook_e2e.py`

Evidence:
  - Webhook e2e tests.
  - Signature failure tests.
  - Setup checklist.

Market-Gate:
  - Real inbound leads can enter the system without manual import.

### T59: Calendar and CRM Live Reconciliation

Owner: human + codex
Phase: 18
Type: provider booking crm
Depends-On: T25, T26, T55

Objective: |
  Add reconciliation for calendar bookings, CRM writes, and outbound messaging provider records so operators can detect missing, duplicated, or failed external records.

Acceptance-Criteria:
  - AC-1: Calendar booking records can be reconciled by provider booking ID and tenant.
  - AC-2: CRM lead records can be reconciled by provider record ID and source event ID.
  - AC-3: Email, WhatsApp, and Telegram send records can be reconciled by provider message ID, channel, tenant, and idempotency key.
  - AC-4: Reconciliation reports missing, duplicate, failed, rate-limited, and stale records without exposing PII in logs.
  - AC-5: Operator-visible retry/handoff path exists for unresolved discrepancies.

Files:
  - `src/lead_sla_agent/tools/calendar.py`
  - `src/lead_sla_agent/tools/crm.py`
  - `src/lead_sla_agent/tools/messaging.py`
  - `src/lead_sla_agent/operator/provider_reconciliation.py`
  - `tests/integration/test_provider_reconciliation.py`

Evidence:
  - Reconciliation tests.
  - Duplicate/missing provider record tests.

Market-Gate:
  - Buyer can trust that booked jobs and CRM records match product analytics.

---

## Phase 19 - Observability and Reliability Operations

Goal: make production behavior visible, alertable, and explainable before broad customer traffic.

### T60: Metrics Backend and Alert Routing

Owner: human + codex
Phase: 19
Type: observability reliability
Depends-On: T40, T53

Objective: |
  Connect the existing metric contract to the chosen metrics backend and define actionable alerts for SLA breaches, provider failures, queue depth, error rate, and unsafe automation blocks.
  Primary backend for the VPS pilot is Grafana Cloud using a Prometheus-compatible `/metrics` export.
  Fallback/self-hosted mode is Prometheus + Alertmanager + Grafana in Docker Compose on the VPS, plus an external uptime check because same-host alerting cannot detect total VPS failure.

Acceptance-Criteria:
  - AC-1: Metrics export path is configured for staging and production as Prometheus text at `/metrics`, scraped by Grafana Alloy/Prometheus agent and sent to Grafana Cloud.
  - AC-2: Alert rules include threshold, owner, severity, customer impact, and first response expectation.
  - AC-3: Alerts use PII-free labels only.
  - AC-4: Alert test or dry run proves routing works to the pilot operator route.
  - AC-5: Fallback self-hosted Prometheus + Alertmanager route is documented for VPS-only operation, with the limitation that external uptime monitoring is still required.

Files:
  - `src/lead_sla_agent/observability/metrics.py`
  - `src/lead_sla_agent/api/app.py`
  - `docs/nfr.md`
  - `docs/runbook.md`
  - `tests/unit/test_alert_contract.py`

Evidence:
  - Alert contract tests.
  - Dry-run alert record.
  - PII label scan.

Market-Gate:
  - Customer-impacting failures page the operator before the buyer reports them.

### T61: Structured Logs, Traces, and PII Redaction Gate

Owner: codex
Phase: 19
Type: observability privacy
Depends-On: T60

Objective: |
  Standardize structured logs and trace context across intake, agent decisions, provider calls, review actions, and background workers with an automated PII redaction gate.

Acceptance-Criteria:
  - AC-1: Logs include correlation ID, tenant ref/hash, component, action, result, and latency when applicable.
  - AC-2: Logs and traces exclude raw email, phone, address, customer name, message body, and secrets.
  - AC-3: Tests fail on known PII patterns in captured logs.
  - AC-4: Runbook explains how to debug an incident using correlation IDs.

Files:
  - `src/lead_sla_agent/observability/logging.py`
  - `docs/runbook.md`
  - `tests/integration/test_log_redaction.py`

Evidence:
  - Captured-log PII tests.
  - Correlation ID tests.

Market-Gate:
  - Support can debug failures without exposing customer data.

### T62: SLO Dashboard and Incident Drill

Owner: human + codex
Phase: 19
Type: reliability support
Depends-On: T60, T61

Objective: |
  Define production SLOs, dashboard panels, incident drill procedure, and customer communication path for the first pilot tenants.

Acceptance-Criteria:
  - AC-1: SLOs cover first response latency, provider send success, webhook intake success, review queue age, and unsafe autonomous-send count.
  - AC-2: Dashboard specification maps each SLO to metric names and alert rules.
  - AC-3: Incident drill template records detection time, mitigation, customer impact, root cause, and prevention.
  - AC-4: Support docs link incident severity to customer update templates.

Files:
  - `docs/nfr.md`
  - `docs/support/runbook.md`
  - `docs/support/incident_template.md`
  - `tests/unit/test_slo_docs.py`

Evidence:
  - SLO docs tests.
  - Incident drill record template.

Market-Gate:
  - Pilot buyers get measurable reliability commitments, not vague uptime claims.

---

## Phase 20 - Security, Privacy, and Compliance Readiness

Goal: reduce launch risk around abuse, data handling, legal promises, and operational access.

### T63: Threat Model and Abuse Protection

Owner: human + codex
Phase: 20
Type: security abuse
Depends-On: T58

Objective: |
  Produce and implement the first production threat model covering webhooks, operator auth, tenant isolation, provider calls, prompt injection, rate limits, replay attacks, and abuse scenarios.

Acceptance-Criteria:
  - AC-1: Threat model lists assets, actors, trust boundaries, top threats, controls, and residual risks.
  - AC-2: Webhook and operator endpoints have documented rate-limit behavior.
  - AC-3: Replay, signature failure, tenant-scope, and prompt-injection controls have tests or eval cases.
  - AC-4: Stop-ship security findings are tracked in Fix Queue until resolved.

Files:
  - `docs/security/threat_model.md`
  - `src/lead_sla_agent/api/`
  - `tests/integration/test_security_controls.py`
  - `docs/agent_eval.md`

Evidence:
  - Threat model.
  - Security-control tests.
  - Agent eval update for prompt injection.

Market-Gate:
  - Founder can answer buyer security questions with concrete controls and known residual risks.

### T64: Privacy, Retention, and Customer Data Terms

Owner: human + codex
Phase: 20
Type: privacy compliance legal
Depends-On: T39, T52

Objective: |
  Align data export/delete/anonymize behavior with plain-language customer terms, privacy policy, retention limits, and DPA-ready operational commitments.

Acceptance-Criteria:
  - AC-1: Privacy docs explain what data is collected, why, retention period, export/delete behavior, and subprocessors.
  - AC-2: Retention jobs or documented manual procedure enforce transcript/audit/export retention expectations.
  - AC-3: Export/delete/anonymize tests verify customer data handling commitments.
  - AC-4: Legal docs avoid promises the system cannot technically honor.

Files:
  - `docs/legal/privacy.md`
  - `docs/legal/dpa_notes.md`
  - `docs/runbook.md`
  - `tests/unit/test_privacy_docs.py`
  - `tests/integration/test_data_retention.py`

Evidence:
  - Privacy docs tests.
  - Retention behavior tests or documented manual drill.

Market-Gate:
  - Paid pilot agreement can include data handling terms the product can actually meet.

### T65: Access Review and Production Admin Controls

Owner: codex
Phase: 20
Type: security ops rbac
Depends-On: T37, T52

Objective: |
  Add production admin access review procedures and role-gated controls for support, tenant owners, operators, viewers, and emergency access.

Acceptance-Criteria:
  - AC-1: Access review report lists tenant users, roles, last activity, and privileged actions without PII.
  - AC-2: Emergency access is time-limited, audited, and documented.
  - AC-3: Role downgrade/removal immediately blocks privileged actions.
  - AC-4: Quarterly access review checklist exists for customer-facing operations.

Files:
  - `src/lead_sla_agent/operator/auth.py`
  - `src/lead_sla_agent/operator/access_review.py`
  - `docs/runbook.md`
  - `tests/integration/test_access_review.py`

Evidence:
  - RBAC removal tests.
  - Emergency access audit tests.
  - Access review export test.

Market-Gate:
  - Customers can be told who has access to their account and how access is reviewed.

---

## Phase 21 - Controlled Pilot Launch

Goal: validate the product on real leads with human approval, tight measurement, and explicit go/no-go criteria.

### T66: First Pilot Tenant Launch Checklist

Owner: human + codex
Phase: 21
Type: pilot launch ops
Depends-On: T55, T57, T58, T60, T64

Objective: |
  Create and execute a launch checklist for the first real pilot tenant covering environment setup, knowledge corpus, provider credentials, operator accounts, support contacts, metrics baseline, and fallback plan.

Acceptance-Criteria:
  - AC-1: Checklist includes pre-launch, launch-day, first-week, and rollback/fallback steps.
  - AC-2: Human approval is required for every outbound message at launch.
  - AC-3: Baseline metrics are captured before traffic is routed.
  - AC-4: Buyer signs off on success criteria and stop criteria before launch.

Files:
  - `docs/pilot/launch_checklist.md`
  - `docs/market/pilot_measurement_plan.md`
  - `docs/runbook.md`
  - `tests/unit/test_pilot_launch_docs.py`

Evidence:
  - Launch checklist tests.
  - Signed-off success/stop criteria artifact.

Market-Gate:
  - First customer can launch with clear safety, support, and measurement expectations.

### T67: Real-Data Eval and Operator Feedback Loop

Owner: human + codex
Phase: 21
Type: eval agent:quality rag:quality tool:safety
Depends-On: T33, T66

Objective: |
  Convert de-identified pilot transcripts and operator corrections into regression evals for retrieval, tool use, and agent policy decisions.

Acceptance-Criteria:
  - AC-1: Feedback export de-identifies customer PII before entering eval fixtures.
  - AC-2: Retrieval eval includes real missed/accepted answers from the pilot.
  - AC-3: Tool eval includes real provider failure and retry cases.
  - AC-4: Agent eval includes real handoff, unsafe, insufficient-evidence, and approved-send cases.
  - AC-5: Eval thresholds are updated only with documented rationale.

Files:
  - `tests/eval/fixtures/`
  - `tests/eval/`
  - `docs/retrieval_eval.md`
  - `docs/tool_eval.md`
  - `docs/agent_eval.md`
  - `tests/eval/test_operator_feedback.py`

Evidence:
  - De-identified eval fixtures.
  - Eval regression results.
  - Threshold rationale.

Market-Gate:
  - Product quality improves from real operator behavior, not synthetic assumptions.

### T67a: Pre-Pilot Evidence Package

Owner: codex
Phase: 21
Type: eval agent:quality rag:quality tool:safety gtm
Depends-On: T66, T74, T75

Objective: |
  Create a claim-safe pre-pilot evidence package that proves controlled scenario
  behavior, baseline comparison, failure handling, and human-approval readiness
  without pretending to have real pilot production data.

Acceptance-Criteria:
  - AC-1: The public/synthetic garage-door scenario fixture has at least 50
    scenarios across at least 10 categories, with expected urgency, action,
    human-approval, and blocked-claim metadata.
  - AC-2: Replay artifacts include controlled agent behavior, baseline
    comparison, and failure-mode results with zero autonomous sends.
  - AC-3: Buyer-facing docs state exactly what is proven, what is not proven,
    and which evidence still requires a real pilot.
  - AC-4: Expert review rubric supports external dispatcher/operator review
    without collecting raw customer PII.
  - AC-5: Tests reject production ROI, live-client proof, autonomous-send
    safety, and paid-readiness claims in the pre-pilot package.

Files:
  - `tests/eval/fixtures/garage_door_leads.json`
  - `scripts/replay_demo_leads.py`
  - `docs/market/pre_pilot_evidence_plan.md`
  - `docs/market/pre_pilot_evidence_report.md`
  - `docs/market/pre_pilot_demo_script.md`
  - `docs/market/expert_review_rubric.md`
  - `docs/market/baseline_comparison.md`
  - `docs/market/failure_mode_replay.md`
  - `docs/market/demo_replays/`
  - `tests/eval/test_pre_pilot_replay.py`
  - `tests/unit/test_pre_pilot_docs.py`

Evidence:
  - Pre-pilot replay reports.
  - Baseline comparison report.
  - Failure-mode replay report.
  - Claim-boundary doc tests.

Market-Gate:
  - Buyer can evaluate a credible pilot ask using controlled evidence, while
    real ROI and live-production claims remain explicitly unproven.

### T68: Autonomous Send Readiness Gate

Owner: human + codex
Phase: 21
Type: safety agent:policy
Depends-On: T67

Objective: |
  Define and enforce the conditions under which a tenant may move selected low-risk replies from human approval to autonomous send.

Acceptance-Criteria:
  - AC-1: Autonomous send remains disabled by default for every tenant.
  - AC-2: Tenant-specific enablement requires owner approval, minimum eval performance, low unsafe/handoff rate, and rollback plan.
  - AC-3: Autonomous categories are narrowly scoped and auditable.
  - AC-4: Any uncertainty, insufficient evidence, provider failure, or policy match routes back to human review.
  - AC-5: Runbook includes immediate kill-switch procedure.

Files:
  - `src/lead_sla_agent/agent/policy.py`
  - `src/lead_sla_agent/operator/tenant_admin.py`
  - `docs/agent_eval.md`
  - `docs/runbook.md`
  - `tests/integration/test_autonomous_send_gate.py`

Evidence:
  - Agent policy tests.
  - Eval threshold evidence.
  - Kill-switch drill.

Market-Gate:
  - Autonomous sending can be discussed with buyers only after measured safety evidence exists.

### T69: Production Readiness Go/No-Go Review

Owner: human + codex
Phase: 21
Type: audit release
Depends-On: T50, T51, T52, T56, T59, T62, T65, T68

Objective: |
  Run a final production-readiness review before broad paid production launch.

Acceptance-Criteria:
  - AC-1: Review covers data durability, deploy/rollback, live providers, observability, security, privacy/legal, pilot metrics, eval results, and support readiness.
  - AC-2: Open P0/P1 findings block production launch.
  - AC-3: P2 findings have owner, due date, and accepted residual-risk rationale.
  - AC-4: Go/no-go decision is recorded with evidence links.

Files:
  - `docs/audit/PRODUCTION_READINESS_REVIEW.md`
  - `docs/audit/AUDIT_INDEX.md`
  - `docs/EVIDENCE_INDEX.md`
  - `docs/CODEX_PROMPT.md`

Evidence:
  - Production readiness review.
  - Full test/lint/eval/CI evidence.
  - Pilot metric summary.

Market-Gate:
  - Product moves from controlled pilot to paid production only with explicit evidence and accepted residual risks.

---

## Recommended Sequence

The highest-leverage path is:

1. Closed baseline: T19-T49 establish durable prototype, provider contracts, AI quality gates, operator workflows, sales readiness, tenant admin, usage metering, and release discipline.
2. Phase 16: persist remaining tenant config, usage billing, and audit ledgers.
3. Phase 17: choose real deployment target and prove staging/prod deploy, smoke, secrets, and rollback.
4. Phase 18: run live provider paths with human approval and reconciliation.
5. Phase 19: connect metrics/logging/alerts and run reliability drills.
6. Phase 20: close security, privacy, legal, access review, and abuse-protection gaps.
7. Phase 21: launch a controlled pilot, feed real data into evals, then run go/no-go readiness review.

Avoid enabling autonomous send or broad paid production before real pilot evidence, rollback rehearsal, alert routing, provider reconciliation, and privacy/legal commitments are proven.

---

## Phase 22 - Solo Public Vertical Showcase

Goal: build a polished, public-source lead-response showcase that a solo
operator can create without customer access. This phase should produce a
vertical knowledge pack, synthetic but evidence-derived lead scenarios, agent
replay artifacts, and a manual outreach package.

Boundary:

- public vertical research is allowed and expected;
- private lead logs, CRM exports, call recordings, inboxes, and paid lead
  portals are not allowed without explicit human approval;
- all generated leads are synthetic/demo unless a customer approves real data;
- if a task lacks enough data, the agent must follow
  `docs/market/open_source_research_protocol.md` and collect public sources
  instead of stopping.

Exit criteria:

- one selected vertical has at least 30 public source records;
- the knowledge pack has source links and unsupported-answer boundaries;
- at least 30 synthetic lead scenarios are generated from public evidence;
- replay artifacts show acknowledgement, qualification, evidence-grounded
  replies, handoff reasons, and unsafe/unsupported behavior;
- a demo report and first-10 manual outreach target list are ready.

### T70: Public Vertical Research Protocol

Owner: codex
Phase: 22
Type: market research
Depends-On: T63

Objective: |
  Document the public vertical research protocol and connect it to pilot/demo
  tasks so future agents gather missing public data safely.

Acceptance-Criteria:
  - AC-1: Protocol lists allowed sources, forbidden sources, source-register
    fields, and claim boundaries.
  - AC-2: Market docs point to the protocol for solo demo-pack work.
  - AC-3: The protocol blocks conversion, ROI, and autonomous-send claims from
    public demo data.

Files:
  - `docs/market/open_source_research_protocol.md`
  - `docs/market/pilot_vertical.md`
  - `docs/market/demo_script.md`

Evidence:
  - Manual doc review.

Market-Gate:
  - The agent can continue public vertical research without private customer
    access.

### T71: Garage Door Public Corpus And Source Register

Owner: codex
Phase: 22
Type: market research rag:ingestion
Depends-On: T70

Objective: |
  Build the first public corpus for the DFW emergency garage door repair wedge:
  companies, service pages, FAQs, service-area pages, booking/contact rules,
  pricing-range evidence, and escalation boundaries.

Acceptance-Criteria:
  - AC-1: Source register contains at least 30 public records from the selected
    vertical.
  - AC-2: Each source record has URL/locator, captured_at, evidence_kind,
    extracted_fact, demo_use, and limitation.
  - AC-3: No private contact data or unsupported ROI claim is committed.

Files:
  - `docs/market/public_corpus/garage_door_repair_source_register.md`
  - `seed/verticals/garage_door_repair/`

Evidence:
  - Source register with links.
  - Public-safe seed corpus.

Market-Gate:
  - Demo knowledge is grounded in public vertical facts instead of invented
    examples.

### T72: Evidence-Derived Synthetic Lead Scenario Bank

Owner: codex
Phase: 22
Type: eval agent:quality
Depends-On: T71

Objective: |
  Create at least 30 synthetic inbound lead scenarios from the public corpus,
  covering routine, urgent, missing-field, unsupported, and risky cases.

Acceptance-Criteria:
  - AC-1: Each synthetic lead cites the public source facts or assumptions that
    shaped it.
  - AC-2: Scenario labels include expected extracted fields, next action,
    handoff reason, and unsafe/unsupported expectation.
  - AC-3: Scenario bank is clearly labeled as synthetic demo data.

Files:
  - `tests/eval/fixtures/garage_door_leads.json`
  - `docs/market/public_corpus/garage_door_scenario_bank.md`
  - `docs/agent_eval.md`

Evidence:
  - Eval fixture.
  - Scenario-bank documentation.

Market-Gate:
  - The demo can show realistic behavior without pretending to have real leads.

### T73: Public Knowledge Pack And Retrieval Eval

Owner: codex
Phase: 22
Type: rag:quality
Depends-On: T71, T72

Objective: |
  Turn the public corpus into a vertical knowledge pack and retrieval eval slice
  for FAQ, service-area, booking, pricing-range, and unsupported-answer cases.

Acceptance-Criteria:
  - AC-1: Knowledge pack entries cite source URLs or mark assumptions.
  - AC-2: Retrieval eval includes supported and unsupported questions.
  - AC-3: Unsupported questions route to insufficient evidence or human review.

Files:
  - `seed/verticals/garage_door_repair/`
  - `tests/eval/fixtures/retrieval_pilot_seed.json`
  - `docs/retrieval_eval.md`

Evidence:
  - Retrieval eval update.
  - Public knowledge pack.

Market-Gate:
  - Demo answers are grounded in approved public knowledge.

### T74: Human-Approval Replay Harness

Owner: codex
Phase: 22
Type: agent:quality tool:safety
Depends-On: T72, T73

Objective: |
  Run the synthetic lead bank through the conversation policy with human
  approval enabled and produce replay artifacts for response, extraction,
  handoff, and no-send behavior.

Acceptance-Criteria:
  - AC-1: Replay output includes transcript, extracted fields, proposed reply,
    evidence IDs, handoff reason, and send/no-send decision.
  - AC-2: Unsafe, unsupported, and low-confidence cases never produce
    autonomous customer-facing send.
  - AC-3: Replay results are reproducible from committed demo fixtures.

Files:
  - `scripts/replay_demo_leads.py`
  - `docs/market/demo_replays/`
  - `tests/eval/test_demo_replay.py`

Evidence:
  - Replay report.
  - Agent/tool eval updates.

Market-Gate:
  - The demo shows safety and operator trust, not only fast generated text.

### T75: Public Demo Report Pack

Owner: codex
Phase: 22
Type: report gtm
Depends-On: T74

Objective: |
  Package the public vertical showcase into a clear report that can be shown in
  manual conversations.

Acceptance-Criteria:
  - AC-1: Report includes vertical corpus summary, scenario coverage, replay
    metrics, examples, safety boundaries, and missing real-pilot evidence.
  - AC-2: Report avoids conversion lift, ROI, and paid-readiness claims.
  - AC-3: Report states exactly what a real pilot would need to prove.

Files:
  - `docs/market/demo_report_garage_door_repair.md`
  - `docs/market/demo_script.md`

Evidence:
  - Demo report.
  - Updated demo script.

Market-Gate:
  - The operator has a showable artifact before asking for real lead data.

### T76: First-10 Manual Outreach Target List

Owner: human + codex
Phase: 22
Type: gtm research
Depends-On: T75

Objective: |
  Create a manually reviewed first-10 target list and conversation plan for the
  selected vertical.

Acceptance-Criteria:
  - AC-1: Target list cites public source pages and why each account is a fit.
  - AC-2: Outreach asks for a narrow replay/pilot conversation, not broad system
    access.
  - AC-3: No automated outreach is executed by the product or agent.

Files:
  - `docs/market/first_10_targets.md`
  - `docs/market/demo_script.md`
  - `docs/market/pilot_terms.md`

Evidence:
  - First-10 list.
  - Manual conversation script.

Market-Gate:
  - Solo operator knows who to contact and what concrete artifact to show.

### T77: Solo Showcase Readiness Review

Owner: human + codex
Phase: 22
Type: audit decision
Depends-On: T75, T76

Objective: |
  Decide whether the public vertical showcase is ready for manual conversations
  and whether to request real lead logs, run a concierge replay, or improve the
  demo pack.

Acceptance-Criteria:
  - AC-1: Review cites corpus, scenario bank, replay artifacts, demo report, and
    first-10 target list.
  - AC-2: Review records no-go conditions and missing real-pilot evidence.
  - AC-3: Review updates `docs/CODEX_PROMPT.md` with the next task.

Files:
  - `docs/audit/SOLO_SHOWCASE_READINESS_REVIEW.md`
  - `docs/CODEX_PROMPT.md`

Evidence:
  - Readiness review.

Market-Gate:
  - The product moves to manual outreach only after the demo pack is coherent
    and claim-safe.

---

## Phase 23 - Pause, Extraction, And Resume Criteria

Goal: stop speculative standalone product development, preserve the useful
engineering patterns, and define the conditions under which this project becomes
active again.

### T78: Pause Decision And README Alignment

Owner: codex
Phase: 23
Type: docs decision
Depends-On: T77

Objective: |
  Record the portfolio decision that Lead Response SLA Agent is paused without
  real business load, and align README/docs so it sells as a reference case
  rather than pretending to be an active SaaS.

Acceptance-Criteria:
  - AC-1: README and `docs/PROJECT_PLAN.md` state paused/reference status.
  - AC-2: Resume criteria require real lead data, pilot operator feedback, or a
    paying workflow.
  - AC-3: No new provider or production-hardening tasks are marked active.

Files:
  - `README.md`
  - `docs/PROJECT_PLAN.md`
  - `docs/CODEX_PROMPT.md`

### T79: Reusable Pattern Extraction Pack

Owner: codex
Phase: 23
Type: docs integration
Depends-On: T78

Objective: |
  Extract reusable lessons for Workflow-To-Agent Studio and AI Workflow
  Playbook: permission boundaries, human approval, idempotent tools, tenant
  isolation, eval fixtures, and rollback evidence.

Acceptance-Criteria:
  - AC-1: Extraction pack maps concrete project artifacts to reusable workflow
    patterns.
  - AC-2: The pack identifies which patterns belong in Workflow-To-Agent Studio,
    Training OS, and AI Workflow Playbook.
  - AC-3: It does not require copying this product's business domain.

Files:
  - `docs/pattern_extraction_pack.md`

### T80: Resume Criteria Review

Owner: human + codex
Phase: 23
Type: review
Depends-On: T79

Objective: |
  Decide whether the project remains paused, becomes a portfolio-only case, or
  resumes due to real business load.

Acceptance-Criteria:
  - AC-1: Review lists current evidence, missing evidence, and resume triggers.
  - AC-2: If no real business data exists, next task remains paused.
  - AC-3: If resumed, the next task must be the smallest real-pilot validation
    step, not broad product expansion.

Files:
  - `docs/audit/PAUSE_AND_RESUME_REVIEW.md`
  - `docs/CODEX_PROMPT.md`
