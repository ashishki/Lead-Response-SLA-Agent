# Evidence Index - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-20

This file indexes durable proof so agents can retrieve prior evidence quickly. It is not authoritative by itself; every row points to the artifact that carries the evidence.

---

## Evidence Table

| Topic / Finding / Task | Artifact type | Location | Scope covered | Last verified | Canonical? |
|------------------------|---------------|----------|---------------|---------------|------------|
| RAG baseline plan | eval | `docs/retrieval_eval.md` | Retrieval metrics, dataset plan, regression policy | 2026-05-19 | Yes |
| Tool-Use baseline plan | eval | `docs/tool_eval.md` | Tool schema and side-effect eval scenarios | 2026-05-19 | Yes |
| Agent loop baseline plan | eval | `docs/agent_eval.md` | Agent termination, handoff, and allowed-action eval scenarios | 2026-05-19 | Yes |
| NFR baseline plan | nfr | `docs/nfr.md` | Latency and operational targets for pilot | 2026-05-19 | Yes |
| RAG reference patterns | reference | `docs/RAG_REFERENCE.md` | Dream Motif Interpreter RAG patterns selected for adaptation | 2026-05-19 | No |
| Active profile eval gates | CI/test | `.github/workflows/ci.yml`, `tests/eval/` | Retrieval, Tool-Use, and Agentic eval gates in CI | 2026-05-19 | Yes |
| Active production task graph | task graph | `docs/tasks.md` | T19-T49 development-loop tasks after completed prototype | 2026-05-19 | Yes |
| Completed prototype task graph | archive | `docs/archive/tasks_T01_T18_completed.md` | Historical T01-T18 task graph and acceptance scope | 2026-05-19 | No |
| Compact loop prompt state | prompt | `docs/CODEX_PROMPT.md`, `docs/prompts/LOOP_TASK_PROMPT.md` | Current next task and per-task loop instructions without completed-task bloat | 2026-05-19 | Yes |
| T19 persistent repositories | integration test | `tests/integration/test_persistent_repositories.py` | PostgreSQL-backed lead, conversation, transcript, review, approval, and outcome persistence plus tenant isolation and PII-safe failures | 2026-05-20 | Yes |
| T20 transactional intake | integration test | `tests/integration/test_transactional_intake.py` | Webhook replay idempotency, transactional rollback on transcript/audit failures, payload-hash-only storage, and intake latency metrics | 2026-05-20 | Yes |
| T21 Redis workers | integration test | `tests/integration/test_redis_workers.py` | Redis-backed SLA breach idempotency, outbound confirmation guard, retry attempt dedupe, and one-time human-review creation | 2026-05-20 | Yes |
| T22 RLS isolation | integration test | `tests/integration/test_rls_tenant_isolation.py`, `alembic/versions/0004_rls_policies.py` | Forced RLS policies for all tenant-scoped tables, cross-tenant direct-query denial, and missing-context fail-closed behavior | 2026-05-20 | Yes |
| T23 backup and migration drill | unit test | `tests/unit/test_runbook_backup_restore.py`, `docs/runbook.md`, `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh` | Backup schedule, restore command and verification checklist, local restore drill, and migration downgrade/rationale checks | 2026-05-20 | Yes |
| Phase 7 verification | review | `docs/audit/PHASE7_REVIEW.md` | T19-T23 same-session verification with persistence, Redis, RLS, and backup/restore evidence | 2026-05-20 | Yes |
| T24 email messaging provider | integration test / eval | `tests/integration/test_messaging_provider.py`, `docs/tool_eval.md` | Email provider adapter with fake HTTP responses, idempotency-key enforcement, provider result recording, secret scope, and unsafe-send gate | 2026-05-20 | Yes |
| T25 calendar provider | integration test / eval | `tests/integration/test_calendar_provider.py`, `docs/tool_eval.md` | Calendar fresh lookup gate, explicit acceptance gate, booking idempotency, timeout human-review fallback, and secret scope | 2026-05-20 | Yes |
| T26 CRM provider | integration test / eval | `tests/integration/test_crm_provider.py`, `docs/tool_eval.md` | CRM create/update idempotency by source event or lead ID, provider-scoped credentials, and failed-write audit/retry path | 2026-05-20 | Yes |
| T27 provider webhooks | integration test | `tests/integration/test_provider_webhooks.py` | Provider-specific email/WhatsApp/Telegram signature matrix, invalid-signature no-write behavior, canonical normalization, and provider ID PII hashing | 2026-05-20 | Yes |
| Phase 8 verification | review | `docs/audit/PHASE8_REVIEW.md` | T24-T27 same-session verification with messaging, calendar, CRM, and provider webhook evidence | 2026-05-20 | Yes |
| T28 production embedding provider | ADR / eval / integration test | `docs/adr/ADR-002-production-embedding-provider.md`, `docs/retrieval_eval.md`, `tests/integration/test_embedding_adapter.py` | OpenAI `text-embedding-3-small` at 1536 dimensions, fake-provider adapter tests, deterministic baseline comparison, and reindex requirement | 2026-05-20 | Yes |
| T29 knowledge admin API | integration test / eval | `tests/integration/test_knowledge_admin.py`, `docs/retrieval_eval.md` | Authenticated upload/list/disable/reindex, active-document exclusion for disabled docs, reindex metadata, and raw-transcript approval guard | 2026-05-20 | Yes |
| T30 pilot retrieval dataset | eval fixture | `tests/eval/fixtures/retrieval_pilot_seed.json`, `tests/eval/test_retrieval_eval.py`, `docs/retrieval_eval.md` | 50 pilot-like questions covering pricing, service area, cancellation, booking, exact terms, unsupported, stale, and tenant isolation slices with PII scan | 2026-05-20 | Yes |
| T31 model and policy versioning | integration test / eval | `tests/integration/test_model_versioning.py`, `docs/agent_eval.md` | Model name, prompt version, schema version, policy decision metadata and unsupported-evidence no-text behavior | 2026-05-20 | Yes |
| Phase 9 verification | review | `docs/audit/PHASE9_REVIEW.md` | T28-T31 same-session verification with embedding, knowledge admin, retrieval eval, and model/policy versioning evidence | 2026-05-20 | Yes |
| T32 operator console API | ADR / integration test | `docs/adr/ADR-003-operator-console-surface.md`, `tests/integration/test_operator_dashboard.py` | Internal JSON console path, review context inspection, approve/edit/send, no-send, action audit fields, outcome labels, and unauthorized access denial | 2026-05-20 | Yes |
| T33 operator feedback eval loop | eval fixture / test | `tests/eval/fixtures/operator_feedback_candidates.json`, `tests/eval/test_operator_feedback.py`, `docs/agent_eval.md`, `docs/retrieval_eval.md`, `docs/tool_eval.md` | De-identified operator feedback export, human approval gate, and accepted retrieval/tool/agent regression partitions | 2026-05-20 | Yes |
| T34 pilot vertical selection | market doc / unit test | `docs/market/pilot_vertical.md`, `docs/market/first_10_targets.md`, `tests/unit/test_market_docs.py` | DFW emergency garage door repair wedge, buyer persona, rejected alternatives, baseline metric hypotheses, public research links, and first 10 targets | 2026-05-20 | Yes |
| T35 garage door vertical pack | seed pack / integration test | `docs/verticals/garage_door_repair.md`, `seed/verticals/garage_door_repair/`, `tests/integration/test_vertical_pack.py`, `docs/retrieval_eval.md` | Required fields, qualification questions, unsafe/handoff policy, operator scripts, seed corpus, retrieval eval cases, and demo tenant initialization | 2026-05-20 | Yes |
| T36 pilot ROI analytics | integration test / nfr | `src/lead_sla_agent/operator/analytics.py`, `tests/integration/test_pilot_analytics.py`, `docs/nfr.md` | Weekly operator analytics API for first-response p50/p95, automation success, human-review rate, booked labels, provider send failures, and markdown report export | 2026-05-20 | Yes |
| T37 production auth and RBAC | integration test | `src/lead_sla_agent/operator/auth.py`, `tests/integration/test_operator_auth_rbac.py` | Signed operator bearer tokens, owner/operator access, viewer denial before data access, tenant-scoped token claims, and generic auth failures | 2026-05-20 | Yes |
| T38 secrets and environment partitioning | unit test / runbook | `compose.yml`, `docs/runbook.md`, `tests/unit/test_secret_policy.py` | Local/staging/production secret sources, adapter-scoped API/worker env vars, high-confidence credential scan, and rotation procedure | 2026-05-20 | Yes |
| T39 data export and delete | integration test / runbook | `src/lead_sla_agent/operator/data_admin.py`, `tests/integration/test_data_export_delete.py`, `docs/runbook.md` | Tenant export schema with PII fields, retention policy, anonymization operation, and `tenant_data_anonymized` audit record | 2026-05-20 | Yes |
| T40 observability and incident runbook | unit/integration test / nfr | `src/lead_sla_agent/observability/metrics.py`, `tests/unit/test_observability_contract.py`, `docs/nfr.md`, `docs/runbook.md` | Stable PII-free metric names/labels, alert thresholds, incident procedures, and health endpoint PII-free coverage | 2026-05-20 | Yes |
| T41 pilot measurement plan | market doc / unit test | `docs/market/pilot_measurement_plan.md`, `docs/market/weekly_report_template.md`, `tests/unit/test_market_docs.py` | Baseline/pilot periods, buyer outcome metrics, weekly report template, and payment/expansion decision gate | 2026-05-20 | Yes |
| T42 pricing and pilot terms | market doc / unit test | `docs/market/pricing.md`, `docs/market/pilot_terms.md`, `tests/unit/test_market_docs.py` | Three pricing hypotheses, lead-value/review-workload alignment, willingness-to-pay script, pilot terms, success criteria, and objection capture | 2026-05-20 | Yes |
| T43 sales proof kit | market doc / unit test | `docs/market/case_study_template.md`, `docs/market/demo_script.md`, `docs/market/objections.md`, `tests/unit/test_market_docs.py` | Case study template, garage-door demo script, and objection handling for safety, data, integration, pricing, attribution, and answering-service competition | 2026-05-20 | Yes |
| T44 assisted onboarding | script / integration test | `scripts/onboard_tenant.py`, `seed/verticals/garage_door_repair/onboarding_questions.json`, `tests/integration/test_onboarding_flow.py`, `docs/runbook.md` | One-working-day onboarding checklist, sandbox provider event, 10-question knowledge validation, and operator approval path | 2026-05-20 | Yes |
| T45 demo tenant sandbox | seed/script/integration test | `seed/demo_tenant/template.json`, `scripts/reset_demo_tenant.py`, `tests/integration/test_demo_tenant.py` | PII-free sales sandbox with supported FAQ, unsupported handoff, booking proposal, operator approval, analytics, and reset command | 2026-05-20 | Yes |
| T46 support process | support docs / unit test | `docs/support/runbook.md`, `docs/support/incident_template.md`, `docs/support/customer_templates.md`, `tests/unit/test_support_docs.py` | Pilot support severity levels, response expectations, escalation, post-incident review, provider outage templates, and AI safety handoff templates | 2026-05-20 | Yes |
| T47 tenant admin configuration | integration test | `src/lead_sla_agent/operator/tenant_admin.py`, `tests/integration/test_tenant_admin.py` | Versioned tenant config updates, safe vs dangerous fields, owner/approval gate, tenant-scoped audit history | 2026-05-20 | Yes |
| T48 usage metering | integration test | `src/lead_sla_agent/billing/usage.py`, `tests/integration/test_usage_metering.py` | Append-only tenant usage events, monthly PII-free export, billing dimensions, active channels, and pricing experiment mapping | 2026-05-20 | Yes |
| T49 release discipline | CI/CD config / unit test | `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`, `docs/runbook.md`, `docs/release_template.md`, `tests/unit/test_ci_workflow.py` | Split CI gates, staging-before-production deploy workflow, migration/smoke checks, release notes, and rollback validation | 2026-05-20 | Yes |
| Phase 10 verification | review | `docs/audit/PHASE10_REVIEW.md` | T32-T33 same-session verification with operator console and feedback eval evidence | 2026-05-20 | Yes |
| Phase 11 verification | review | `docs/audit/PHASE11_REVIEW.md` | T34-T36 same-session verification with pilot vertical, vertical pack, and ROI analytics evidence | 2026-05-20 | Yes |
| Phase 12 verification | review | `docs/audit/PHASE12_REVIEW.md` | T37-T40 same-session verification with auth/RBAC, secrets, privacy export/delete, and observability evidence | 2026-05-20 | Yes |
| Phase 13 verification | review | `docs/audit/PHASE13_REVIEW.md` | T41-T43 same-session verification with measurement, pricing, pilot terms, and sales proof kit evidence | 2026-05-20 | Yes |
| Phase 14 verification | review | `docs/audit/PHASE14_REVIEW.md` | T44-T46 same-session verification with assisted onboarding, demo sandbox, and support process evidence | 2026-05-20 | Yes |
| Phase 15 verification | review | `docs/audit/PHASE15_REVIEW.md` | T47-T49 same-session verification with tenant admin, usage metering, and release discipline evidence | 2026-05-20 | Yes |
| Bootstrap decisions | decision log | `docs/DECISION_LOG.md` | Initial solution shape, profiles, runtime, retrieval mode, approval boundaries | 2026-05-19 | No |
| Bootstrap handoff | journal note | `docs/IMPLEMENTATION_JOURNAL.md` | Session-level continuity for the generated Phase 1 package | 2026-05-19 | No |

---

## Retrieval Rules

- Prefer rows that match the current task's `Context-Refs`, open findings, or active profile tags.
- If an evidence row points to a stale or missing artifact, fix the artifact or remove the row.
- Do not treat a journal note as proof when a test, eval, or review report exists.
