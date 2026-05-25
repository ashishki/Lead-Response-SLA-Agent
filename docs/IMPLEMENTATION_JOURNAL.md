# Implementation Journal - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-23
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

### 2026-05-23 - T66 - First Pilot Tenant Launch Checklist

- Scope: `docs/pilot/launch_checklist.md`, `docs/market/pilot_measurement_plan.md`, `docs/runbook.md`, `tests/unit/test_pilot_launch_docs.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T66 required a first real pilot tenant launch checklist covering setup, baseline metrics, human approval, fallback, and buyer signoff.
- Decisions applied: first pilot starts with one approved inbound source, one approved outbound channel, and human approval for every outbound message.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_pilot_launch_docs.py tests/unit/test_market_docs.py -q --tb=short` -> 21 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 255 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; checklist includes pre-launch, launch-day, first-week, rollback/fallback steps, human approval at launch, baseline metric capture before traffic, and buyer success/stop signoff.
- Follow-ups: T67 is blocked until approved real pilot data exists.
- Notes for next agent: do not synthesize T67 real-data evals from public/demo fixtures; wait for de-identified pilot transcripts, operator corrections, provider failures, and approval metadata.

### 2026-05-23 - Phase 20 Review - Security, Privacy, and Compliance Readiness

- Scope: T63-T65, `docs/audit/PHASE20_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: Phase 20 tasks completed and the orchestrator requires a phase-boundary review before continuing.
- Decisions applied: continue to Phase 21 T66 because verification is green and no stop condition remains.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 251 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Follow-ups: continue to T66 First Pilot Tenant Launch Checklist.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-23 - T65 - Access Review and Production Admin Controls

- Scope: `src/lead_sla_agent/operator/access_review.py`, `tests/integration/test_access_review.py`, `docs/runbook.md`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T65 required production admin access review procedures and role-gated controls.
- Decisions applied: access review exports hash actor refs; privileged actions re-check current role/status; emergency access is bounded to 1-240 minutes and audited.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_access_review.py tests/integration/test_operator_auth_rbac.py -q --tb=short` -> 8 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 251 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; report lists roles, last activity, and privileged actions without PII; emergency access is time-limited/audited; role downgrade/removal blocks privileged actions immediately; quarterly checklist is documented.
- Follow-ups: complete Phase 20 review, then continue to T66.
- Notes for next agent: wire `AccessReviewStore.authorize` into any new privileged admin route rather than trusting long-lived role claims alone.

### 2026-05-23 - T64 - Privacy, Retention, and Customer Data Terms

- Scope: `docs/legal/privacy.md`, `docs/legal/dpa_notes.md`, `docs/runbook.md`, `src/lead_sla_agent/operator/data_admin.py`, `tests/unit/test_privacy_docs.py`, `tests/integration/test_data_retention.py`, `tests/integration/test_data_export_delete.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: user approved resuming T64 customer-facing privacy/legal/retention/subprocessor wording after Phase 22 completed.
- Decisions applied: v1 customer delete remains anonymization, not hard deletion; retention enforcement scrubs expired PII while preserving operational counts and append-only audit records.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_privacy_docs.py tests/integration/test_data_export_delete.py tests/integration/test_data_retention.py -q --tb=short` -> 10 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 247 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; privacy docs explain collected data, purpose, retention, export/delete behavior, and subprocessors; runbook documents retention enforcement; tests verify anonymization/export/retention behavior and block unsupported hard-delete promises.
- Follow-ups: continue to T65 Access Review and Production Admin Controls.
- Notes for next agent: customer-facing docs intentionally avoid hard deletion, zero retention, SOC 2/HIPAA/GDPR certification, autonomous send, and unspecified subprocessor promises.

### 2026-05-23 - T77 - Solo Showcase Readiness Review

- Scope: `docs/audit/SOLO_SHOWCASE_READINESS_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `tests/unit/test_market_docs.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T77 required deciding whether the public vertical showcase is ready for manual conversations and recording no-go conditions plus missing real-pilot evidence.
- Decisions applied: `D-012`, `docs/market/open_source_research_protocol.md`, and Phase 22 readiness gates.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 241 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found the Phase 22 public showcase ready for founder-led manual conversations, not autonomous send, paid production, conversion claims, ROI claims, or real customer data intake.
- Follow-ups: no active Codex implementation task; next non-Codex step is founder-led manual outreach. T64 remains deferred pending human legal/privacy approval.
- Notes for next agent: do not resume T64 or customer-facing privacy/terms work without human approval.

### 2026-05-23 - T76 - First-10 Manual Outreach Target List

- Scope: `docs/market/first_10_targets.md`, `docs/market/demo_script.md`, `docs/market/pilot_terms.md`, `tests/unit/test_market_docs.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T76 required a manually reviewed first-10 target list and conversation plan for the selected vertical.
- Decisions applied: `D-012` and `docs/market/open_source_research_protocol.md`.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 16 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 240 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; target list cites public source pages and `GD-PUB-*` records, asks for a narrow replay/pilot conversation, and explicitly forbids automated outreach.
- Follow-ups: continue to T77 Solo Showcase Readiness Review.
- Notes for next agent: pre-pilot outreach must stay manual and must not request private lead data on first touch.

### 2026-05-23 - T75 - Public Demo Report Pack

- Scope: `docs/market/demo_report_garage_door_repair.md`, `docs/market/demo_script.md`, `tests/unit/test_market_docs.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T75 required packaging the public vertical showcase into a showable report for manual conversations.
- Decisions applied: `D-012` and `docs/market/open_source_research_protocol.md`.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 15 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 239 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; report includes corpus summary, scenario coverage, replay metrics, examples, safety boundaries, missing real-pilot evidence, and proof plan while blocking conversion, ROI, autonomous-send, and paid-readiness claims.
- Follow-ups: continue to T76 First-10 Manual Outreach Target List.
- Notes for next agent: demo script now points to the report and asks for a narrow real pilot proof conversation.

### 2026-05-23 - T74 - Human-Approval Replay Harness

- Scope: `scripts/replay_demo_leads.py`, `docs/market/demo_replays/garage_door_replay_report.json`, `docs/market/demo_replays/garage_door_replay_report.md`, `tests/eval/test_demo_replay.py`, `docs/agent_eval.md`, `docs/tool_eval.md`, `tests/eval/test_agent_eval.py`, `tests/eval/test_tool_eval.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T74 required replaying the synthetic lead bank with human approval enabled and producing reproducible replay artifacts.
- Decisions applied: `D-012`, `docs/market/open_source_research_protocol.md`, and `conversation-policy-v1` boundaries.
- Evidence collected: `.venv/bin/python -m pytest tests/eval/test_demo_replay.py tests/eval/test_agent_eval.py tests/eval/test_tool_eval.py -q --tb=short` -> 10 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 237 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; each replay includes transcript, extracted fields, proposed-reply field, evidence IDs, handoff reason, and send/no-send decision; unsafe/unsupported cases have zero autonomous sends.
- Follow-ups: continue to T75 Public Demo Report Pack.
- Notes for next agent: replay script is deterministic and intentionally does not call messaging, booking, CRM, calendar, LLM, retrieval, or provider adapters.

### 2026-05-23 - T73 - Public Knowledge Pack And Retrieval Eval

- Scope: `seed/verticals/garage_door_repair/corpus.json`, `seed/verticals/garage_door_repair/retrieval_eval.json`, `tests/integration/test_vertical_pack.py`, `docs/retrieval_eval.md`, `tests/eval/test_retrieval_eval.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T73 required turning the public garage-door corpus into source-cited knowledge-pack entries and a retrieval eval slice.
- Decisions applied: `D-012` and `docs/market/open_source_research_protocol.md`.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_vertical_pack.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 234 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; public knowledge-pack documents include source record IDs and URLs, retrieval eval includes supported and unsupported public questions, and unsupported public claims route to insufficient evidence or human review.
- Follow-ups: continue to T74 Human-Approval Replay Harness.
- Notes for next agent: public-source knowledge is demo/seed evidence only; tenant-specific service areas, pricing, and booking commitments still require approved tenant policy.

### 2026-05-23 - T72 - Evidence-Derived Synthetic Lead Scenario Bank

- Scope: `tests/eval/fixtures/garage_door_leads.json`, `docs/market/public_corpus/garage_door_scenario_bank.md`, `docs/agent_eval.md`, `tests/eval/test_agent_eval.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T72 required at least 30 synthetic inbound lead scenarios derived from public corpus evidence.
- Decisions applied: `D-012` and `docs/market/open_source_research_protocol.md`.
- Evidence collected: `.venv/bin/python -m pytest tests/eval/test_agent_eval.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 233 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; scenario fixture contains 30 synthetic demo leads with cited public source IDs or assumptions, expected extracted fields, next action, handoff reason, and unsafe/unsupported expectation; raw contact PII scan passes.
- Follow-ups: continue to T73 Public Knowledge Pack And Retrieval Eval.
- Notes for next agent: the scenario bank is eval/demo material only and cannot support conversion, ROI, autonomous-send, or paid-readiness claims.

### 2026-05-23 - T71 - Garage Door Public Corpus And Source Register

- Scope: `docs/market/public_corpus/garage_door_repair_source_register.md`, `seed/verticals/garage_door_repair/public_corpus.json`, `tests/unit/test_market_docs.py`, `docs/retrieval_eval.md`, `tests/eval/test_retrieval_eval.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T71 required a public source register and seed corpus for the DFW emergency garage door repair wedge.
- Decisions applied: `D-012` and `docs/market/open_source_research_protocol.md`.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 18 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 229 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; source register contains 35 public records with required fields, no private contact data, and no unsupported ROI/conversion claims; public corpus JSON links source IDs and keeps approved retrieval corpus unchanged until T73.
- Follow-ups: continue to T72 Evidence-Derived Synthetic Lead Scenario Bank.
- Notes for next agent: T72 scenarios should cite `GD-PUB-*` source IDs or explicit assumptions and remain synthetic demo data.

### 2026-05-23 - T70 - Public Vertical Research Protocol

- Scope: `docs/market/open_source_research_protocol.md`, `docs/market/pilot_vertical.md`, `docs/market/demo_script.md`, `tests/unit/test_market_docs.py`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T70 required a public-source protocol so the solo demo-pack phase can continue without private customer access.
- Decisions applied: `D-012`.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 11 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 227 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; protocol lists allowed/forbidden sources, required source-register fields, and claim boundaries; pilot/demo docs link the protocol; conversion, ROI, autonomous-send, and paid-readiness claims remain blocked until real pilot evidence exists.
- Follow-ups: continue to T71 Garage Door Public Corpus And Source Register.
- Notes for next agent: source-register rows must include `pii_contact_handling`; public research can support demo artifacts but cannot prove customer ROI or autonomous-send safety.

### 2026-05-21 - T63 - Threat Model and Abuse Protection

- Scope: `docs/security/threat_model.md`, `src/lead_sla_agent/api/rate_limit.py`, `src/lead_sla_agent/api/app.py`, `src/lead_sla_agent/api/webhooks.py`, `src/lead_sla_agent/operator/api.py`, `src/lead_sla_agent/operator/knowledge_api.py`, `src/lead_sla_agent/conversation/loop.py`, `tests/integration/test_security_controls.py`, `docs/agent_eval.md`, `tests/eval/test_agent_eval.py`.
- Why this work happened: user approved proceeding with security-boundary work for the VPS pilot.
- Decisions applied: added in-process per-client rate limits for the single-VPS pilot, documented that Redis-backed limits are required before multi-process/multi-node scaling, and made prompt-injection-like messages fail closed to human review without customer-facing drafts.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_security_controls.py tests/eval/test_agent_eval.py tests/integration/test_provider_webhooks.py tests/integration/test_operator_review.py tests/integration/test_knowledge_admin.py -q --tb=short` -> 20 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 251 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no open stop-ship security findings; threat model covers assets, actors, trust boundaries, top threats, controls, residual risks, and rate-limit behavior; tests cover rate limits, signature failure, replay idempotency, tenant-scoped operator access, and prompt-injection handoff.
- Follow-ups: T64 is blocked pending human approval of privacy/legal wording, retention promises, and subprocessor commitments.
- Notes for next agent: rate limiting is intentionally in-process for the current single-process VPS assumption; move counters to Redis before running multiple API workers or VPS instances.

### 2026-05-21 - Phase 19 Review - Observability and Reliability Operations

- Scope: T60-T62, `docs/audit/PHASE19_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 19 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: stop before T63 because threat modeling, rate limits, replay controls, and prompt-injection handling are security-boundary work requiring human approval.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 245 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Follow-ups: T63 is blocked pending human approval to change/lock security-boundary behavior.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-21 - T62 - SLO Dashboard and Incident Drill

- Scope: `docs/nfr.md`, `docs/support/runbook.md`, `docs/support/incident_template.md`, `tests/unit/test_slo_docs.py`.
- Why this work happened: T62 required measurable reliability commitments, dashboard mappings, incident drill procedure, and customer communication path.
- Decisions applied: documented pilot SLOs for first-response latency, provider send success, webhook intake success, review queue age, and unsafe autonomous-send count; mapped each SLO to metric names, alert rules, dashboard panels, and operator actions; added incident drill fields and severity-to-template routing.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_slo_docs.py tests/unit/test_support_docs.py tests/unit/test_nfr_doc.py tests/unit/test_alert_contract.py -q --tb=short` -> 13 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 245 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; SLOs cover the required production behaviors, dashboard specification maps each SLO to metric names and alert rules, incident drill template records detection/mitigation/customer impact/root cause/prevention, and support docs link severity to customer update templates.
- Follow-ups: complete Phase 19 review, then stop before T63 for human security-boundary approval.
- Notes for next agent: SLOs are explicitly pilot operational targets, not contractual uptime promises.

### 2026-05-21 - T61 - Structured Logs, Traces, and PII Redaction Gate

- Scope: `src/lead_sla_agent/observability/logging.py`, `src/lead_sla_agent/observability/pii.py`, `docs/runbook.md`, `tests/integration/test_log_redaction.py`.
- Why this work happened: T61 required structured log context and automated PII redaction for production debugging.
- Decisions applied: added correlation ID context helpers, structured log event emission with tenant hash/component/action/result/latency/trace ID fields, recursive PII scrubbing for structured fields, string-level email/phone redaction, and runbook guidance for correlation-ID incident debugging.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_log_redaction.py tests/unit/test_pii_scrubber.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 242 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; captured logs include correlation ID, tenant hash, component, action, result, latency, and trace ID while excluding raw emails, phones, customer names, addresses, message bodies, provider IDs, tokens, and secrets.
- Follow-ups: continue to T62 SLO Dashboard and Incident Drill.
- Notes for next agent: logging helpers are available but not yet wired through every runtime path; T62 can document the operational dashboard while T63+ can broaden runtime adoption.

### 2026-05-21 - T60 - Metrics Backend and Alert Routing

- Scope: `src/lead_sla_agent/observability/metrics.py`, `src/lead_sla_agent/api/app.py`, `docs/tasks.md`, `docs/nfr.md`, `docs/runbook.md`, `tests/unit/test_alert_contract.py`, `tests/unit/test_observability_contract.py`.
- Why this work happened: user approved Grafana Cloud with Prometheus-compatible metrics as the best-practice alerting path for the VPS pilot.
- Decisions applied: selected Grafana Cloud as the primary metrics/alert backend, Prometheus-compatible `/metrics` as the app export format, Grafana Alloy/Prometheus agent as the VPS scrape/remote-write path, and Prometheus + Alertmanager + Grafana as the same-host fallback that still requires an external uptime check.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_alert_contract.py tests/unit/test_observability_contract.py tests/integration/test_health.py -q --tb=short` -> 12 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 238 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; staging/production export targets use `/metrics`, alert rules include threshold/owner/severity/customer impact/first response expectation, labels are PII-free, and `alert_dry_run("provider_send_failure_rate_high")` routes to `pilot_operator`.
- Follow-ups: continue to T61 Structured Logs, Traces, and PII Redaction Gate.
- Notes for next agent: the exporter is intentionally Prometheus text without adding a new dependency; Grafana Cloud credentials are not committed and are represented only as deployment/runbook configuration.

### 2026-05-21 - Phase 18 Review - Live Provider Production Readiness

- Scope: T57-T59, `docs/audit/PHASE18_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 18 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: stop before T60 because choosing the metrics backend and alert route is a human+Codex observability/operations decision for the VPS pilot.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 232 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Follow-ups: T60 is blocked pending human selection/approval of the metrics backend and alert route for the VPS pilot.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-21 - T59 - Calendar, CRM, and Messaging Provider Reconciliation

- Scope: `src/lead_sla_agent/operator/provider_reconciliation.py`, `tests/integration/test_provider_reconciliation.py`, `docs/CODEX_PROMPT.md`, `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: T59 required reconciliation for calendar bookings, CRM writes, and outbound message provider records after live provider paths were defined.
- Decisions applied: added a deterministic PII-free reconciliation module for expected versus observed provider records; records are keyed by tenant, provider type, idempotency key, and channel; discrepancy types cover missing, duplicate, failed, rate-limited, and stale records; operator actions expose only operational references.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_provider_reconciliation.py tests/integration/test_calendar_provider.py tests/integration/test_crm_provider.py tests/integration/test_live_messaging_contract.py -q --tb=short` -> 19 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 232 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; calendar booking reconciliation uses provider booking IDs and idempotency keys, CRM reconciliation uses remote record/source event IDs, message reconciliation covers email/WhatsApp/Telegram by provider message status and channel, tenant scope is enforced in keys, and operator actions contain no lead PII.
- Follow-ups: complete Phase 18 review, then stop before T60 until the human chooses/approves the metrics backend and alert route.
- Notes for next agent: `provider_reconciliation.py` is intentionally pure/deterministic and does not call external providers; T60 can use its discrepancy counts for alert routing later.

### 2026-05-21 - T58 - Provider Webhook End-to-End Drill

- Scope: `src/lead_sla_agent/api/webhooks.py`, `src/lead_sla_agent/intake/signatures.py`, `src/lead_sla_agent/intake/normalizer.py`, `docs/runbook.md`, `tests/integration/test_provider_webhook_e2e.py`.
- Why this work happened: T58 required public webhook e2e proof for email, WhatsApp, and Telegram after the live outbound provider matrix was selected.
- Decisions applied: added provider aliases for `postmark_email`, `twilio_whatsapp`, and `telegram_bot`; extended the in-memory webhook store to create transcript hash records and PII-free review task references; documented VPS reverse proxy setup, provider signature headers, Telegram secret-token handling, and WhatsApp opt-in metadata.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_provider_webhook_e2e.py tests/integration/test_provider_webhooks.py tests/integration/test_webhook_intake.py -q --tb=short` -> 15 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 228 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; invalid provider signatures reject before writes, replayed provider event IDs are idempotent across the derived workflow objects, transcript storage uses hashes rather than raw message text, review tasks are PII-free references, and runbook setup avoids token logging.
- Follow-ups: continue to T59 Calendar and CRM Live Reconciliation.
- Notes for next agent: `InMemoryWebhookStore.row_counts()` intentionally preserves the older four-table contract; new e2e checks use `workflow_counts()` for transcript/review task coverage.

### 2026-05-21 - T57 - Live Messaging Provider Pilot Path

- Scope: `docs/tasks.md`, `src/lead_sla_agent/tools/messaging.py`, `src/lead_sla_agent/workers/retries.py`, `src/lead_sla_agent/config.py`, `docs/runbook.md`, `tests/integration/test_live_messaging_contract.py`, `tests/unit/test_environment_secret_contract.py`.
- Why this work happened: user confirmed the pilot needs email, WhatsApp, and Telegram, then asked to detail the tasks and continue implementation.
- Decisions applied: expanded Phase 18 tasks for Postmark email, Twilio WhatsApp, and Telegram Bot API; implemented a common live outbound messaging contract with provider/channel metadata, Postmark/Twilio/Telegram adapters using injectable HTTP transports, pilot human-approval default, WhatsApp opt-in enforcement, Telegram chat-initiation enforcement, rate-limit handling, and retry/handoff metrics without requiring live credentials in normal tests.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_live_messaging_contract.py tests/integration/test_messaging_provider.py tests/integration/test_provider_adapters.py tests/unit/test_environment_secret_contract.py tests/integration/test_sla_queue.py -q --tb=short` -> 22 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 222 passed after starting isolated PostgreSQL/Redis containers; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; live credentials are scoped by adapter and not needed by tests, pilot sends default to human approval across all channels, provider results record metadata and rate-limit flags, WhatsApp requires opt-in metadata, Telegram requires a user-initiated chat ID, and provider failures create retry/handoff without duplicate review tasks.
- Follow-ups: continue to T58 Provider Webhook End-to-End Drill.
- Notes for next agent: test containers `lead-sla-test-postgres` and `lead-sla-test-redis` were started on ports 55432 and 6380 for full verification.

### 2026-05-20 - Phase 17 Review - Deployment Hardening

- Scope: T53-T56, `docs/audit/PHASE17_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 17 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: stop before T57 because choosing the first live messaging provider and live credential path is a human+Codex provider/security-boundary decision.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 215 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Follow-ups: T57 is blocked pending human selection/approval of the first live messaging provider for the pilot.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-20 - T56 - Rollback Rehearsal and Migration Safety

- Scope: `scripts/rollback_check.py`, `docs/rollback_rehearsal.md`, `docs/runbook.md`, `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`, `tests/unit/test_rollback_rehearsal.py`.
- Why this work happened: T56 required turning rollback documentation into a rehearsed, testable command path before production promotion.
- Decisions applied: added AST-based migration downgrade coverage checks, explicit irreversible-rationale support, a staging rehearsal artifact with before/after migration version fields, and production workflow validation before deployment starts.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_rollback_rehearsal.py tests/unit/test_runbook_backup_restore.py tests/unit/test_ci_workflow.py tests/unit/test_deployment_target_docs.py -q --tb=short` -> 21 passed; `.venv/bin/python scripts/rollback_check.py --rehearsal-artifact docs/rollback_rehearsal.md --json` -> `ok: true`; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 215 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; all current migrations have downgrade coverage, rehearsal artifact records before/after migration versions, runbook defines app-only versus migration versus backup restore decisions, and production workflow validates rollback artifacts before deploying.
- Follow-ups: complete Phase 17 review, then stop before T57 until the human chooses/approves the first live messaging provider.
- Notes for next agent: `docs/rollback_rehearsal.md` is a template artifact; the real release operator should fill the TBD fields per staging release rehearsal.

### 2026-05-20 - T55 - Deployment Smoke Tests

- Scope: `scripts/smoke_test.py`, `.github/workflows/deploy.yml`, `docs/runbook.md`, `tests/integration/test_smoke_tests.py`, `tests/unit/test_deployment_target_docs.py`.
- Why this work happened: T55 required a real post-deploy smoke command for VPS staging and production promotion.
- Decisions applied: added a CLI that targets staging or production by URL/environment, checks API health, Alembic migration version, Redis, operator auth, provider sandbox, and unsafe-message handoff; sandbox provider sends use only `FakeMessagingAdapter` and `sandbox@example.test`, with provider smoke skipped unless `--sandbox-mode` is explicit.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_smoke_tests.py tests/unit/test_deployment_target_docs.py tests/unit/test_ci_workflow.py -q --tb=short` -> 20 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 208 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; production deployment depends on staging smoke success, smoke checks fail closed when `DATABASE_URL` or `REDIS_URL` is missing, and no real customer send path is used.
- Follow-ups: continue to T56 Rollback Rehearsal and Migration Safety.
- Notes for next agent: deploy workflow runs smoke from inside the API container with `http://localhost:8000`; real VPS setup must ensure the API container can reach itself at that address.

### 2026-05-20 - T54 - Staging and Production Secret Partitioning

- Scope: `src/lead_sla_agent/config.py`, `docs/runbook.md`, `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`, `tests/unit/test_environment_secret_contract.py`.
- Why this work happened: T54 required explicit environment-specific secret expectations for VPS staging and production without committing credentials.
- Decisions applied: added a config-level secret contract for local/staging/production API, worker, and deploy runtimes; provider credentials are scoped by adapter; deploy workflow validates secret names and remote `.env` key presence without printing values.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_environment_secret_contract.py tests/unit/test_secret_policy.py tests/unit/test_deployment_docs.py tests/unit/test_deployment_target_docs.py tests/unit/test_ci_workflow.py -q --tb=short` -> 24 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 199 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; required secrets are documented separately for local/staging/production, missing-secret errors list names only, provider credentials are scoped per adapter, and rotation includes revocation verification.
- Follow-ups: continue to T55 Deployment Smoke Tests.
- Notes for next agent: deploy workflow checks remote `.env` key names with `grep -q` and does not echo secret values.

### 2026-05-20 - T53 - Deployment Target ADR and Infrastructure Contract

- Scope: `docs/adr/ADR-004-deployment-target.md`, `docs/runbook.md`, `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`, `alembic.ini`, `alembic/env.py`, `tests/unit/test_deployment_target_docs.py`.
- Why this work happened: T53 required a human-approved first production hosting target and concrete deployment/rollback commands.
- Decisions applied: user selected VPS as simpler and more understandable; ADR-004 accepts VPS with Docker Compose, preserves T1 runtime, rejects Render/Railway/AWS ECS for the first pilot, and assigns founder/operator ownership for host operations.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_deployment_target_docs.py tests/unit/test_deployment_docs.py tests/unit/test_ci_workflow.py -q --tb=short` -> 15 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/alembic upgrade head` -> passed after disposable test schema reset; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 194 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; ADR names VPS/Docker Compose and rejected alternatives, runtime remains T1, staging/prod resources include owner/backup/retention/cost expectations, deploy workflow uses SSH to VPS with Docker Compose migration/smoke commands, and rollback command validation is documented/tested.
- Follow-ups: continue to T54 Staging and Production Secret Partitioning.
- Notes for next agent: `alembic.ini` and async `alembic/env.py` were added as adjacent support because the prior workflow command was not runnable without a script location and DATABASE_URL-aware async engine.

### 2026-05-20 - Phase 16 Review - Production Data Durability

- Scope: T50-T52, `docs/audit/PHASE16_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 16 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: stop before T53 because deployment target selection is a human+Codex architecture decision.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 188 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Follow-ups: T53 is blocked pending human selection/approval of the first production deployment target.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-20 - T52 - Immutable Audit Event Store

- Scope: `src/lead_sla_agent/audit/events.py`, `src/lead_sla_agent/db/audit_repository.py`, `src/lead_sla_agent/db/models.py`, `alembic/versions/0007_audit_events.py`, `docs/runbook.md`, `tests/integration/test_audit_event_store.py`, and adjacent flow hooks in tenant admin, usage, review, and data admin paths.
- Why this work happened: T52 required a centralized tenant-scoped audit event store for operational actions before production use.
- Decisions applied: added canonical `audit_log_event` rows with actor ref, action, resource type/id, result, policy version, timestamp, and PII-free payload; owner/operator roles can search audit events, viewer cannot.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_audit_event_store.py tests/integration/test_tenant_admin_persistence.py tests/integration/test_usage_metering_persistence.py tests/integration/test_persistent_repositories.py tests/unit/test_db_models.py -q --tb=short` -> 22 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 188 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; audit events are append-only through the repository API, reject PII/secrets, search is tenant-scoped and role-gated, RLS denies cross-tenant direct reads, and tenant admin, billing usage, review approval, and data admin flows emit canonical audit fields.
- Follow-ups: complete Phase 16 review, then stop before T53 until the human chooses the deployment target.
- Notes for next agent: provider-send audit is covered by the canonical repository event shape; live provider wiring can attach to it when provider execution moves to persistent flows.

### 2026-05-20 - T51 - Persistent Usage and Billing Event Ledger

- Scope: `src/lead_sla_agent/billing/usage.py`, `src/lead_sla_agent/db/usage_repository.py`, `src/lead_sla_agent/db/models.py`, `alembic/versions/0006_usage_ledger.py`, `tests/integration/test_usage_metering.py`, `tests/integration/test_usage_metering_persistence.py`, `tests/unit/test_db_models.py`.
- Why this work happened: T51 required replacing usage metering's in-memory-only contract with an append-only PostgreSQL ledger for billing exports and reconciliation.
- Decisions applied: added `usage_ledger_event` with tenant/event-id uniqueness, RLS, persistent event-id idempotency, deterministic monthly export regeneration, PII value rejection for metadata, and `pricing-package-mapping-v1` in exports and persisted rows.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_usage_metering.py tests/integration/test_usage_metering_persistence.py tests/unit/test_db_models.py -q --tb=short` -> 12 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 182 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; ledger rows are tenant-scoped, duplicate event IDs do not inflate totals, monthly exports regenerate deterministically after restart, unsupported/PII metadata is rejected, and pricing package mapping is versioned.
- Follow-ups: continue to T52 Immutable Audit Event Store.
- Notes for next agent: Alembic CLI upgrade was not run because the repo has no Alembic config with `script_location`; migration behavior is covered by import-based tests and direct PostgreSQL metadata/RLS tests.

### 2026-05-20 - T50 - Persistent Tenant Configuration Store

- Scope: `src/lead_sla_agent/operator/tenant_admin.py`, `src/lead_sla_agent/db/tenant_config_repository.py`, `src/lead_sla_agent/db/models.py`, `alembic/versions/0005_tenant_config.py`, `tests/integration/test_tenant_admin_persistence.py`, `tests/unit/test_db_models.py`.
- Why this work happened: T50 required replacing tenant admin's in-memory-only configuration contract with durable PostgreSQL-backed versioned storage.
- Decisions applied: added `tenant_config` current-state rows plus append-only `tenant_config_audit` rows; retained the existing safe/dangerous field policy gate and added optimistic `expected_version` conflict detection.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_tenant_admin.py tests/integration/test_tenant_admin_persistence.py tests/unit/test_db_models.py -q --tb=short` -> 11 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 176 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; config survives new sessions, mutations create new versions and audit rows, dangerous changes require owner/approval, stale versions conflict, and repository/RLS tenant isolation is covered.
- Follow-ups: continue to T51 Persistent Usage and Billing Event Ledger.
- Notes for next agent: an Alembic CLI upgrade check was not run because the repo has no Alembic config with `script_location`; migration behavior is covered by import-based tests and direct PostgreSQL metadata/RLS tests.

### 2026-05-20 - Production Readiness Backlog - T50-T69

- Scope: `docs/tasks.md`, `docs/CODEX_PROMPT.md`, `docs/EVIDENCE_INDEX.md`.
- Why this work happened: user requested detailed development phases that move the current pilot-ready MVP toward production readiness.
- Decisions applied: defined five production-hardening phases plus controlled pilot launch: data durability, deployment/environment hardening, live provider readiness, observability/reliability operations, security/privacy/compliance readiness, and pilot/go-no-go review.
- Evidence collected: documentation-only change; loop state now points to T50 as the next task.
- Follow-ups: implement T50 Persistent Tenant Configuration Store.
- Notes for next agent: T19-T49 remain completed; T50-T69 are the new active production-readiness backlog.

### 2026-05-20 - Phase 15 Review - Multi-Tenant SaaS Scale

- Scope: T47-T49, `docs/audit/PHASE15_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 15 tasks completed and the orchestrator requires a phase-boundary verification artifact before closing the active task graph.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 170 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Follow-ups: active task graph T19-T49 is complete.
- Notes for next agent: this was a same-session verification pass, not an independent review.

### 2026-05-20 - T49 - Staging and Production Release Discipline

- Scope: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`, `docs/runbook.md`, `docs/release_template.md`, `tests/unit/test_ci_workflow.py`, `tests/unit/test_ci_eval_gates.py`, `tests/unit/test_deployment_docs.py`.
- Why this work happened: T49 required staging/prod separation, migration policy, CI/CD gates, release notes, and rollback validation.
- Decisions applied: split CI into lint/format, unit, integration, eval, and deployment checks; added manual deployment workflow with staging-before-production promotion; documented release notes and rollback validation.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_ci_eval_gates.py tests/unit/test_ci_workflow.py tests/unit/test_deployment_docs.py -q --tb=short` -> 10 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 170 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; CI distinguishes unit, integration, eval, and deployment checks; deploy workflow runs staging migrations/smoke tests before production and validates rollback assets.
- Follow-ups: complete Phase 15 review.
- Notes for next agent: workflows define release discipline but still need real environment secrets and deployment commands before production use.

### 2026-05-20 - T48 - Usage Metering and Billing Readiness

- Scope: `src/lead_sla_agent/billing/usage.py`, `tests/integration/test_usage_metering.py`.
- Why this work happened: T48 required tenant-scoped usage dimensions for pricing and billing readiness.
- Decisions applied: implemented append-only usage events and PII-safe monthly exports that map usage to Recovery Pilot, Booked-Lead Share, and Dispatcher Assist pricing experiments.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_usage_metering.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 167 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; exports count leads processed, AI-assisted replies, provider sends, review tasks, bookings, active channels, and provider sends by provider; PII metadata is rejected.
- Follow-ups: continue to T49 Staging/Production Release Discipline.
- Notes for next agent: usage meter is in-memory and should be backed by persistent append-only storage before paid production billing.

### 2026-05-20 - T47 - Tenant Admin and Configuration

- Scope: `src/lead_sla_agent/operator/tenant_admin.py`, `tests/integration/test_tenant_admin.py`.
- Why this work happened: T47 required tenant admin configuration for channels, business hours, required fields, max turns, handoff policy, and provider settings.
- Decisions applied: implemented an in-memory versioned tenant config store; safe fields can be updated by operator role, dangerous policy/autonomous changes require owner role or approval ID, and every change appends an audit event.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_tenant_admin.py -q --tb=short` -> 4 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 162 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; safe updates version config, dangerous changes require owner or approval, unknown fields are rejected, and audit history is tenant-scoped.
- Follow-ups: continue to T48 Usage Metering and Billing Readiness.
- Notes for next agent: store is in-memory policy contract and should be backed by persistent configuration storage before multi-customer production.

### 2026-05-20 - Phase 14 Review - Sales-Ready MVP

- Scope: T44-T46, `docs/audit/PHASE14_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 14 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 158 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Follow-ups: continue to T47 Tenant Admin and Configuration.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T46 - Support and Operations Process

- Scope: `docs/support/runbook.md`, `docs/support/incident_template.md`, `docs/support/customer_templates.md`, `tests/unit/test_support_docs.py`.
- Why this work happened: T46 required a support process for pilot customers: issue intake, severity, response SLA, escalation, post-incident review, incident template, and customer templates.
- Decisions applied: support docs require PII-free incident notes and customer updates; Sev1 includes unsafe autonomous reply, data exposure, customer-facing outage, or all lead intake blocked.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_support_docs.py -q --tb=short` -> 3 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 158 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; severity levels, first-response expectations, escalation paths, incident template, provider outage templates, and AI safety handoff templates are present.
- Follow-ups: complete Phase 14 review, then continue to T47 Tenant Admin and Configuration.
- Notes for next agent: support process is a pilot runbook and should be wired into ticketing only after first paying customers.

### 2026-05-20 - T45 - Demo Tenant and Sales Sandbox

- Scope: `seed/demo_tenant/template.json`, `scripts/reset_demo_tenant.py`, `tests/integration/test_demo_tenant.py`.
- Why this work happened: T45 required a safe demo tenant with seed leads, corpus, review tasks, analytics, and reset command for repeatable sales calls.
- Decisions applied: demo state uses synthetic scenario records and contact refs only; reset script writes a known state from template and can target a temp path for tests or sales setup.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_demo_tenant.py -q --tb=short` -> 4 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 155 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; demo contains supported FAQ, unsupported handoff, booking proposal, and operator approval scenarios; PII scan passes; reset command restores known state.
- Follow-ups: continue to T46 Support and Operations Process.
- Notes for next agent: default reset output is `seed/demo_tenant/state.json`; tests write to temporary output paths to avoid repo churn.

### 2026-05-20 - T44 - Assisted Onboarding Workflow

- Scope: `scripts/onboard_tenant.py`, `seed/verticals/garage_door_repair/onboarding_questions.json`, `tests/integration/test_onboarding_flow.py`, `docs/runbook.md`.
- Why this work happened: T44 required a guided setup flow for tenant creation, provider connection, knowledge upload, operator accounts, and test lead validation.
- Decisions applied: implemented a deterministic sandbox onboarding CLI that uses the garage-door vertical pack, hashes operator email, validates at least 10 tenant knowledge questions, simulates provider send/receive, and tests operator approval path without real provider credentials.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_onboarding_flow.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 151 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; checklist fits within one working day, provider sandbox passes, 10 tenant questions validate against approved corpus, and operator approval path returns sent status.
- Follow-ups: continue to T45 Demo Tenant and Sales Sandbox.
- Notes for next agent: onboarding CLI intentionally outputs hashed operator email only.

### 2026-05-20 - Phase 13 Review - Revenue Validation

- Scope: T41-T43, `docs/audit/PHASE13_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 13 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 146 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T44 Assisted Onboarding Workflow.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T43 - Case Study and Sales Proof Kit

- Scope: `docs/market/case_study_template.md`, `docs/market/demo_script.md`, `docs/market/objections.md`, `tests/unit/test_market_docs.py`.
- Why this work happened: T43 required a buyer-facing proof kit from pilot metrics and operator feedback.
- Decisions applied: proof kit frames the sale around missed-revenue recovery, faster response, safe human review, and garage-door-specific workflows rather than generic AI novelty.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 146 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; case study template includes baseline/intervention/result/quote, demo script maps to garage-door pain, and objections cover safety, data, integration, pricing, attribution, and current answering-service competition.
- Follow-ups: complete Phase 13 review, then continue to T44 Assisted Onboarding Workflow.
- Notes for next agent: proof docs intentionally contain template blanks until a real pilot produces metrics and a buyer quote.

### 2026-05-20 - T42 - Pricing and Packaging Experiment

- Scope: `docs/market/pricing.md`, `docs/market/pilot_terms.md`, `tests/unit/test_market_docs.py`.
- Why this work happened: T42 required pricing hypotheses aligned with lead value/review workload and draft pilot contract terms with success criteria.
- Decisions applied: created three packages to test: Recovery Pilot, Booked-Lead Share, and Dispatcher Assist; pricing is anchored to recovered booked jobs and review workload rather than AI usage.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 6 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 143 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; pricing doc includes at least two package hypotheses, review workload adjustment, willingness-to-pay discovery script, and pricing decision log; pilot terms include commercial terms, buyer/provider responsibilities, success criteria, stop criteria, and objections to capture.
- Follow-ups: continue to T43 Case Study and Sales Proof Kit.
- Notes for next agent: pricing is not validated until at least one buyer accepts pilot terms or gives a clear objection to address.

### 2026-05-20 - T41 - Pilot Measurement Plan

- Scope: `docs/market/pilot_measurement_plan.md`, `docs/market/weekly_report_template.md`, `tests/unit/test_market_docs.py`.
- Why this work happened: T41 required a before/after measurement plan for the first pilot and a weekly buyer report template.
- Decisions applied: measurement is framed around buyer-visible outcomes: response time, lead capture, booked calls/jobs, qualified handoffs, human-review rate, cost per lead, provider failures, and unsafe automation.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 4 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 141 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; baseline and pilot periods are defined, required metrics are documented, and the weekly report template includes scorecard, revenue/labor, safety/quality, and buyer decision sections.
- Follow-ups: continue to T42 Pricing and Packaging Experiment.
- Notes for next agent: buyer must agree before launch that the metric set justifies payment, expansion, or cancellation.

### 2026-05-20 - Phase 12 Review - Security, Reliability, and Compliance Baseline

- Scope: T37-T40, `docs/audit/PHASE12_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 12 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 139 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T41 Pilot Measurement Plan.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T40 - Production Observability and Incident Runbook

- Scope: `src/lead_sla_agent/observability/metrics.py`, `docs/nfr.md`, `docs/runbook.md`, `tests/unit/test_observability_contract.py`.
- Why this work happened: T40 required stable PII-free metrics, documented alert thresholds, incident runbook coverage, and continued PII-free health behavior.
- Decisions applied: added a metric contract with PII-free labels and alert thresholds for latency, send failures, SLA breaches, retrieval freshness, insufficient evidence, tool failures, queue depth, and dependency health.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_observability_contract.py tests/integration/test_health.py tests/integration/test_metrics.py -q --tb=short` -> 7 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 139 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; NFR docs list stable metrics and alert thresholds, runbook covers provider outage, retrieval regression, queue backlog, and webhook signature failures, and health tests remain PII-free.
- Follow-ups: complete Phase 12 review, then continue to T41 Pilot Measurement Plan.
- Notes for next agent: metric labels use `tenant_hash` rather than raw tenant or lead identifiers.

### 2026-05-20 - T39 - Data Retention, Export, and Delete

- Scope: `src/lead_sla_agent/operator/data_admin.py`, `docs/runbook.md`, `tests/integration/test_data_export_delete.py`.
- Why this work happened: T39 required tenant-level data export and deletion/anonymization procedures aligned with pilot privacy expectations.
- Decisions applied: implemented v1 anonymization rather than hard deletion so operational counts and audit history survive while direct customer identifiers are removed.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_data_export_delete.py -q --tb=short` -> 4 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 135 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; export includes leads, conversations, transcripts, audit events, outcomes, review tasks, retention policy, and PII fields; anonymization redacts lead PII and appends `tenant_data_anonymized` audit event.
- Follow-ups: continue to T40 Production Observability and Incident Runbook.
- Notes for next agent: `TenantDataAdmin` is an in-memory policy contract and should be backed by SQL repositories before real customer data export/delete operations.

### 2026-05-20 - T38 - Secrets Management and Environment Partitioning

- Scope: `compose.yml`, `docs/runbook.md`, `tests/unit/test_secret_policy.py`, `tests/unit/test_deployment_docs.py`.
- Why this work happened: T38 required separate local/staging/production secrets, adapter-scoped runtime access, real-credential fixture/doc rejection, and rotation documentation.
- Decisions applied: API receives only inbound/auth/database variables; worker receives provider adapter and retrieval secrets but not webhook or operator auth secrets; unused LLM/Telegram/WhatsApp vars were removed from Compose runtime scope.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_secret_policy.py tests/unit/test_deployment_docs.py -q --tb=short` -> 7 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 131 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; runbook documents source and rotation for every runtime secret, Compose environment scopes are exact, and docs/fixtures are scanned for common real credential shapes.
- Follow-ups: continue to T39 Data Retention, Export, and Delete Procedures.
- Notes for next agent: the secret scanner intentionally targets high-confidence credential patterns to avoid false positives on test placeholders and hashes.

### 2026-05-20 - T37 - Production Operator Auth and RBAC

- Scope: `src/lead_sla_agent/operator/auth.py`, `src/lead_sla_agent/config.py`, `tests/integration/test_operator_auth_rbac.py`, adjacent operator route compatibility tests.
- Why this work happened: T37 required replacing literal test bearer auth with authenticated principal parsing and tenant/role authorization for operator routes.
- Decisions applied: implemented signed bearer tokens carrying actor, tenant, role, and optional expiry claims; owner/operator roles can access operator routes, viewer receives 403 before data access, and invalid/expired tokens receive generic 401 responses.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_operator_auth_rbac.py tests/integration/test_operator_review.py tests/integration/test_operator_dashboard.py tests/integration/test_knowledge_admin.py tests/integration/test_pilot_analytics.py -q --tb=short` -> 19 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 127 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; owner and operator tokens work, viewer is denied before store access, tenant token claims scope returned data, and auth failures expose only `unauthorized`.
- Follow-ups: continue to T38 Secrets Management and Environment Partitioning.
- Notes for next agent: `OPERATOR_TEST_TOKEN` remains available for existing tests but is now a signed operator token generated by the auth module.

### 2026-05-20 - Phase 11 Review - Pilot Vertical Package

- Scope: T34-T36, `docs/audit/PHASE11_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 11 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 123 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T37 Production Auth and RBAC.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - Phase 10 Review - Operator UX and Feedback Loop

- Scope: T32-T33, `docs/audit/PHASE10_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`.
- Why this work happened: Phase 10 was completed before Phase 11 and needed its phase-boundary verification artifact.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 123 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: none
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T36 - Pilot ROI Analytics

- Scope: `src/lead_sla_agent/operator/analytics.py`, `src/lead_sla_agent/operator/api.py`, `tests/integration/test_pilot_analytics.py`, `docs/nfr.md`, `tests/unit/test_nfr_doc.py`.
- Why this work happened: T36 required a dashboard/API reporting first-response latency p50/p95, automation success, human-review rate, booked labels, provider send failures, and weekly report export.
- Decisions applied: implemented a tenant-scoped in-memory analytics store and authenticated operator endpoint as the pilot reporting contract; persistent aggregation can replace the store later.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_pilot_analytics.py tests/unit/test_nfr_doc.py -q --tb=short` -> 4 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 123 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; sample weekly report includes p50=3000 ms, p95=10000 ms, automation success rate=0.50, human-review rate=0.25, booked outcomes=1, and provider send failures=1.
- Follow-ups: complete Phase 11 review, then continue to T37 Production Auth and RBAC.
- Notes for next agent: current analytics source is an in-memory event store for pilot tests, not production SQL rollup.

### 2026-05-20 - T35 - Garage Door Vertical Policy Pack

- Scope: `docs/verticals/garage_door_repair.md`, `seed/verticals/garage_door_repair/`, `src/lead_sla_agent/verticals.py`, `tests/integration/test_vertical_pack.py`, `docs/retrieval_eval.md`, `tests/eval/test_retrieval_eval.py`.
- Why this work happened: T35 required a reusable vertical configuration pack with lead fields, qualification questions, unsafe categories, handoff reasons, operator scripts, seed corpus, eval dataset, and demo tenant initialization.
- Decisions applied: used a file-based `vertical-pack-v1` seed structure so founder/operators can inspect and edit the vertical corpus and policies without code changes.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_vertical_pack.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 8 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 120 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; the pack includes five approved corpus documents, six vertical retrieval eval cases, required fields/questions, unsafe handoff categories, and a demo tenant initializer.
- Follow-ups: continue to T36 Pilot ROI Dashboard.
- Notes for next agent: vertical eval cases are seed coverage, not live retrieval quality over a production vector index.

### 2026-05-20 - T34 - Pilot Vertical and Buyer Persona

- Scope: `docs/market/pilot_vertical.md`, `docs/market/first_10_targets.md`, `tests/unit/test_market_docs.py`.
- Why this work happened: T34 required selecting one time-sensitive service vertical and defining buyer persona, lead sources, response pain, value hypothesis, rejected alternatives, baseline metrics, and first 10 targets.
- Decisions applied: selected DFW emergency/same-day garage door repair as the first validation wedge; rejected broader HVAC, plumbing, roofing, med spa, and legal intake as heavier first pilots.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_market_docs.py -q --tb=short` -> 2 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 117 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; market docs include public research links, metric hypotheses, rejected alternatives, and 10 named target accounts with outreach channels.
- Follow-ups: continue to T35 Vertical Policy Pack.
- Notes for next agent: baseline metrics in T34 are hypotheses to replace with buyer-provided call logs, form timestamps, and booking data.

### 2026-05-20 - T33 - Operator Feedback to Eval Candidates

- Scope: `src/lead_sla_agent/operator/feedback.py`, `tests/eval/fixtures/operator_feedback_candidates.json`, `tests/eval/test_operator_feedback.py`, `docs/agent_eval.md`, `docs/retrieval_eval.md`, `docs/tool_eval.md`.
- Why this work happened: T33 required converting approved/rejected operator decisions into de-identified eval candidates for retrieval, tool, and agent regressions.
- Decisions applied: feedback candidates are exported with hashed draft/message fields and de-identified eval-target text; only entries with human approval metadata are eligible for canonical regression partitions.
- Evidence collected: `.venv/bin/python -m pytest tests/eval/test_operator_feedback.py tests/eval/test_retrieval_eval.py tests/eval/test_tool_eval.py tests/eval/test_agent_eval.py -q --tb=short` -> 13 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 115 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; fixture partitions include one accepted retrieval candidate, one accepted tool candidate, and one accepted agent candidate; unapproved feedback is excluded.
- Follow-ups: continue to T34 Select First Pilot Vertical and Buyer Persona.
- Notes for next agent: `contains_direct_pii` is intended for free-text eval targets, not for whole candidate JSON containing hashes and timestamps.

### 2026-05-20 - T32 - Operator Console API Workflow

- Scope: `src/lead_sla_agent/operator/api.py`, `src/lead_sla_agent/operator/review_queue.py`, `tests/integration/test_operator_dashboard.py`, `tests/integration/test_persistent_repositories.py`, `docs/adr/ADR-003-operator-console-surface.md`, `docs/DECISION_LOG.md`.
- Why this work happened: T32 required the first operator surface for review queue inspection, evidence/transcript references, approve/edit/send, no-send, and outcome labels.
- Decisions applied: ADR-003 selects the authenticated internal JSON operator API as the first pilot console surface instead of introducing a frontend before workflow stabilization.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_operator_dashboard.py tests/integration/test_operator_review.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 110 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; operator review listing exposes lead summary, transcript refs, evidence IDs, proposed reply, and required action; approve/edit/send and no-send actions record actor, timestamp, hashes, reason code, and final status.
- Follow-ups: continue to T33 Feedback Loop from Operator Outcomes to Eval Fixtures.
- Notes for next agent: approval now marks persistent review tasks as `sent`; no-send marks tasks as `no_send`.

### 2026-05-20 - Phase 9 Review - LLM and Retrieval Productionization

- Scope: T28-T31, `docs/audit/PHASE9_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 9 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 105 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T32 Operator Dashboard or Production Console.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T31 - Prompt, Model, and Policy Version Tracking

- Scope: `src/lead_sla_agent/conversation/model_io.py`, `src/lead_sla_agent/conversation/policy.py`, `src/lead_sla_agent/conversation/loop.py`, `docs/agent_eval.md`, `tests/integration/test_model_versioning.py`.
- Why this work happened: T31 required versioned prompt/model/schema/policy contracts for model-like outputs and safety decisions.
- Decisions applied: deterministic runtime outputs now carry `deterministic-runtime-v1`, prompt versions, `model-output-schema-v1`, and `conversation-policy-v1` decisions in audit events.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_model_versioning.py tests/eval/test_agent_eval.py tests/integration/test_conversation_loop.py -q --tb=short` -> 7 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 105 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; every model-like output path tested stores model/prompt/schema/policy metadata, and insufficient evidence still terminates through human review with no outbound draft.
- Follow-ups: complete Phase 9 review.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T30 - Retrieval Eval Dataset Expansion from Pilot Questions

- Scope: `tests/eval/fixtures/retrieval_pilot_seed.json`, `docs/retrieval_eval.md`, `tests/eval/test_retrieval_eval.py`.
- Why this work happened: T30 required retrieval evals to expand from synthetic seed cases to at least 50 pilot-like questions with required scenario slices and no raw customer PII.
- Decisions applied: added a synthetic pilot-like fixture modeled on transcript/operator-feedback scenarios rather than raw customer transcripts; eval row is classified `eval-change-induced`.
- Evidence collected: `.venv/bin/python -m pytest tests/eval/test_retrieval_eval.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 102 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; dataset has 50 questions, all required slices are present, eval row includes required metadata, and fixture PII scan passes.
- Follow-ups: continue to T31 Prompt, Model, and Policy Version Tracking.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T29 - Tenant Knowledge Admin API

- Scope: `src/lead_sla_agent/operator/knowledge_api.py`, `src/lead_sla_agent/retrieval/ingestion.py`, `src/lead_sla_agent/api/app.py`, `tests/integration/test_knowledge_admin.py`, `docs/retrieval_eval.md`.
- Why this work happened: T29 required authenticated operator upload/list/disable/reindex APIs for tenant-approved knowledge documents.
- Decisions applied: implemented an in-memory tenant-scoped admin store that records reindex metadata and excludes disabled documents from active retrieval inputs; persistent knowledge storage remains a later productionization concern.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_knowledge_admin.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 99 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; routes require auth, disabled docs are excluded from reindex active counts, reindex records actor/timestamp/corpus/index schema, and raw transcript uploads require explicit approved-knowledge marking.
- Follow-ups: continue to T30 Retrieval Eval Dataset Expansion from Pilot Questions.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T28 - Production Embedding Adapter Selection

- Scope: `src/lead_sla_agent/retrieval/embeddings.py`, `src/lead_sla_agent/config.py`, `docs/adr/ADR-002-production-embedding-provider.md`, `docs/retrieval_eval.md`, `docs/DECISION_LOG.md`, `tests/integration/test_embedding_adapter.py`.
- Why this work happened: T28 required selecting and implementing a production text embedding provider while preserving fake/deterministic embeddings for normal tests.
- Decisions applied: ADR-002 selects OpenAI `text-embedding-3-small` at 1536 dimensions for v1; model or dimension changes require a new ADR, full reindex plan, and retrieval eval update.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_embedding_adapter.py tests/eval/test_retrieval_eval.py -q --tb=short` -> 5 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 96 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; normal tests use fake provider responses, live provider usage is not in the default suite, retrieval eval compares deterministic baseline to the production embedding configuration baseline, and RAG mode remains text-only.
- Follow-ups: continue to T29 Tenant Knowledge Admin API.
- Notes for next agent: official OpenAI docs were checked for embedding dimensions and model metadata; temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - Phase 8 Review - Real Provider Integrations

- Scope: T24-T27, `docs/audit/PHASE8_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 8 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 93 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T28 Production Embedding Adapter Selection.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T27 - Provider Webhook Verification Matrix

- Scope: `src/lead_sla_agent/intake/signatures.py`, `src/lead_sla_agent/intake/normalizer.py`, `src/lead_sla_agent/api/webhooks.py`, `tests/integration/test_provider_webhooks.py`.
- Why this work happened: T27 required provider-specific webhook signature verification and normalization with no writes on invalid signatures and provider identifiers treated as PII in observability.
- Decisions applied: preserved the generic signature path and added explicit provider schemes for email, WhatsApp, and Telegram behind `X-Lead-SLA-Provider`.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_provider_webhooks.py tests/integration/test_webhook_intake.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 93 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; invalid provider signatures write no rows, normalized events preserve tenant/source/channel/timestamp/hash, and provider user/message IDs are hashed by the PII scrubber.
- Follow-ups: complete Phase 8 review.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T26 - CRM or Spreadsheet Destination Adapter

- Scope: `src/lead_sla_agent/tools/crm.py`, `tests/integration/test_crm_provider.py`, `docs/tool_eval.md`.
- Why this work happened: T26 required the first lead destination adapter with idempotent create/update writes, provider-scoped credentials, and failure handling that does not block safe customer acknowledgement.
- Decisions applied: implemented a CRM/spreadsheet HTTP adapter with injected transport and in-memory idempotency mapping for provider tests; failures return a retry-required result with a PII-safe audit event.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_crm_provider.py tests/eval/test_tool_eval.py tests/integration/test_provider_adapters.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 87 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; duplicate writes return existing mappings by source event or lead ID, CRM settings are adapter-scoped, and failed writes record retry/handoff audit data without raw lead PII.
- Follow-ups: continue to T27 Provider Webhook Verification Matrix.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T25 - Calendar Lookup and Booking Provider Adapter

- Scope: `src/lead_sla_agent/tools/calendar.py`, `tests/integration/test_calendar_provider.py`, `docs/tool_eval.md`.
- Why this work happened: T25 required a calendar provider adapter with fresh-slot lookup, explicit acceptance, booking idempotency, and timeout fallback.
- Decisions applied: HTTP transport is injected so normal tests use fake provider responses and no live credentials; provider timeout returns `human_review_required` with a machine-readable failure reason.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_calendar_provider.py tests/eval/test_tool_eval.py tests/integration/test_provider_adapters.py -q --tb=short` -> 9 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 83 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; bookings reject stale/missing lookup and missing acceptance, duplicate idempotency keys return the existing booking, timeout fallback is recorded, and tool eval is current.
- Follow-ups: continue to T26 CRM or Spreadsheet Destination Adapter.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T24 - First Real Messaging Provider Adapter

- Scope: `src/lead_sla_agent/tools/messaging.py`, `src/lead_sla_agent/config.py`, `tests/integration/test_messaging_provider.py`, `docs/tool_eval.md`.
- Why this work happened: T24 required the first production messaging adapter with provider-scoped secrets, fake-provider tests, idempotent sends, provider result recording, and unsafe-message review gating.
- Decisions applied: implemented email as the first provider adapter because deployment already declares email-specific runtime variables; HTTP transport is injected so normal tests require no live credentials or network provider.
- Evidence collected: `.venv/bin/python -m pytest tests/integration/test_messaging_provider.py tests/eval/test_tool_eval.py -q --tb=short` -> 7 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 79 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; adapter reads only email-specific settings, sends require idempotency keys, success/failure results record provider message ID/status/latency/failure reason, and unsafe messages route to review before provider execution.
- Follow-ups: continue to T25 Calendar Lookup and Booking Provider Adapter.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - Phase 7 Review - Persistence and Runtime Hardening

- Scope: T19-T23, `docs/audit/PHASE7_REVIEW.md`, `docs/audit/AUDIT_INDEX.md`, `docs/CODEX_PROMPT.md`.
- Why this work happened: Phase 7 tasks completed and the orchestrator requires a phase-boundary verification artifact before continuing.
- Decisions applied: none
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 74 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Follow-ups: continue to T24 First Real Messaging Provider Adapter.
- Notes for next agent: this was a same-session verification pass, not independent review.

### 2026-05-20 - T23 - Backup, Restore, and Migration Drill

- Scope: `docs/runbook.md`, `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh`, `tests/unit/test_runbook_backup_restore.py`.
- Why this work happened: T23 required documented backup/restore procedures, a local restore drill path, and migration safety checks.
- Decisions applied: backup and restore scripts are environment-driven through `DATABASE_URL`, `BACKUP_PATH`, and optional `VERIFY_COMMAND`; no credentials are stored in scripts or tests.
- Evidence collected: `.venv/bin/python -m pytest tests/unit/test_runbook_backup_restore.py tests/unit/test_deployment_docs.py -q --tb=short` -> 6 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 74 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; runbook documents backup schedule, restore command, verification checklist, local restore drill, and migration downgrade/rationale checks.
- Follow-ups: complete Phase 7 review.
- Notes for next agent: temporary PostgreSQL and Redis containers on ports 55432 and 6380 were removed after verification.

### 2026-05-20 - T22 - Row-Level Security and Tenant Isolation Drill

- Scope: `alembic/versions/0004_rls_policies.py`, `src/lead_sla_agent/db/tenant.py`, `tests/integration/test_rls_tenant_isolation.py`.
- Why this work happened: T22 required PostgreSQL RLS policies for tenant-scoped tables and proof that direct SQL cannot cross tenant boundaries or read without tenant context.
- Decisions applied: used hardcoded migration statements for each tenant table to avoid dynamic DDL construction; tests switch to a non-BYPASSRLS app role because the local Docker `POSTGRES_USER` owns tables and bypasses RLS by default.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_rls_tenant_isolation.py -q --tb=short` -> 4 passed against isolated local PostgreSQL; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 71 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; all tenant-scoped tables have enabled and forced RLS, cross-tenant direct selects return no rows under app role, missing tenant context fails closed, and tenant context remains transaction-local through parameterized `set_config`.
- Follow-ups: continue to T23 Backup, Restore, and Migration Drill.
- Notes for next agent: T22 was verified with temporary `pgvector/pgvector:pg16` and `redis:7-alpine` containers on ports 55432 and 6380, both removed after verification.

### 2026-05-20 - T21 - Redis-Backed SLA Timers and Provider Retry Workers

- Scope: `src/lead_sla_agent/workers/queue.py`, `src/lead_sla_agent/workers/sla.py`, `src/lead_sla_agent/workers/retries.py`, `tests/integration/test_redis_workers.py`.
- Why this work happened: T21 required Redis-backed async workers for first-response SLA breach marking and provider retry exhaustion with duplicate-delivery idempotency.
- Decisions applied: preserved deterministic in-memory helpers for existing tests and added Redis-backed atomic/idempotent functions using only `redis.asyncio`.
- Evidence collected: `REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/integration/test_redis_workers.py -q --tb=short` -> 3 passed against isolated local Redis; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ -q --tb=short` -> 67 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; SLA breach marking uses Redis atomic `SET ... NX` within a Lua script, retry failure events are deduped by event key, review creation is one-time per lead, and Redis access remains async-only.
- Follow-ups: continue to T22 Row-Level Security and Tenant Isolation Drill.
- Notes for next agent: T21 was verified with temporary `pgvector/pgvector:pg16` and `redis:7-alpine` containers on ports 55432 and 6380, both removed after verification.

### 2026-05-20 - T20 - Transactional Intake and Idempotent Event Processing

- Scope: `src/lead_sla_agent/api/webhooks.py`, `src/lead_sla_agent/intake/lead_service.py`, `src/lead_sla_agent/db/repositories.py`, `src/lead_sla_agent/db/models.py`, `alembic/versions/0003_provider_event_lead_links.py`, `tests/integration/test_transactional_intake.py`.
- Why this work happened: T20 required signed webhook intake to commit provider event, lead, conversation, transcript, and audit rows atomically while replaying source event IDs without duplicate workload.
- Decisions applied: added provider-event lead/conversation foreign keys as adjacent scope because durable replay needs to return original lead and conversation IDs; retained the in-memory webhook store for existing lightweight API tests.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_transactional_intake.py -q --tb=short` -> 3 passed against isolated local PostgreSQL; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/ -q --tb=short` -> 64 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; replay returns existing provider/lead/conversation IDs, transcript and audit failures roll back all new intake rows, raw webhook payloads are not persisted, and intake latency is recorded.
- Follow-ups: continue to T21 Redis-Backed SLA Timers and Provider Retry Workers.
- Notes for next agent: T20 was verified with a temporary `pgvector/pgvector:pg16` container on port 55432 because port 5432 is occupied locally by another Postgres instance with different credentials.

### 2026-05-20 - T19 - Persistent Repositories

- Scope: `src/lead_sla_agent/db/lead_repository.py`, `src/lead_sla_agent/db/transcript_repository.py`, `src/lead_sla_agent/operator/review_queue.py`, `src/lead_sla_agent/operator/outcomes.py`, `src/lead_sla_agent/db/models.py`, `alembic/versions/0002_review_outcome_repositories.py`, `tests/integration/test_persistent_repositories.py`, adjacent API/workflow tenant propagation.
- Why this work happened: T19 required async SQLAlchemy persistence for lead, conversation, transcript, review task, approval, and outcome repository paths with tenant isolation and PII-safe failure behavior.
- Decisions applied: added model and migration files as adjacent scope because review, approval, and outcome persistence tables did not exist; preserved in-memory compatibility for existing API/runtime tests while adding session-backed repository mode.
- Evidence collected: `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/integration/test_persistent_repositories.py -q --tb=short` -> 3 passed against isolated local PostgreSQL; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test .venv/bin/python -m pytest tests/ -q --tb=short` -> 61 passed; `.venv/bin/ruff check src/lead_sla_agent tests alembic` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic` -> passed.
- Verification pass: same-session verification found no P0/P1 findings; tenant context is transaction-local through parameterized `set_config`, cross-tenant reads return no rows, write failures use PII-safe repository exceptions, and runtime tier remains T1.
- Follow-ups: continue to T20 Transactional Intake and Idempotent Event Processing.
- Notes for next agent: port 5432 on this machine is occupied by `ai-rollout-test-postgres` with different credentials; T19 was verified with a temporary `pgvector/pgvector:pg16` container on port 55432 and that container was removed after verification.

### 2026-05-19 - Docs - Production Loop Backlog Setup

- Scope: `docs/tasks.md`, `docs/CODEX_PROMPT.md`, `docs/prompts/ORCHESTRATOR.md`, `docs/prompts/LOOP_TASK_PROMPT.md`, `docs/archive/`, `docs/EVIDENCE_INDEX.md`
- Why this work happened: the production-readiness strategy needed to become an active AI development-loop backlog without bloating prompts.
- Decisions applied: keep active prompts compact; archive completed T01-T18 task and prompt history; make T19 the next active task.
- Evidence collected: documentation sanity checks only; no product code changed.
- Follow-ups: start T19 when implementation resumes.
- Notes for next agent: use `docs/tasks.md` for T19-T49 and read archived T01-T18 details only when historical evidence is needed.

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

### 2026-05-25 - T67a - Pre-Pilot Evidence Package

- Scope: `tests/eval/fixtures/garage_door_leads.json`, `scripts/replay_demo_leads.py`, `docs/market/pre_pilot_evidence_plan.md`, `docs/market/pre_pilot_evidence_report.md`, `docs/market/pre_pilot_demo_script.md`, `docs/market/expert_review_rubric.md`, `docs/market/baseline_comparison.md`, `docs/market/failure_mode_replay.md`, `docs/market/demo_replays/`, `tests/eval/test_pre_pilot_replay.py`, `tests/unit/test_pre_pilot_docs.py`, `docs/agent_eval.md`, `docs/tool_eval.md`
- Why this work happened: T67 real-data eval is blocked until approved real pilot artifacts exist, so the project needed a claim-safe alternative that proves controlled pilot readiness without pretending to have live production data.
- Decisions applied: keep T67 blocked for real pilot transcripts/operator corrections/provider failures; use T67a only for controlled public/synthetic evidence; require human approval for every replay.
- Evidence collected: `.venv/bin/python scripts/replay_demo_leads.py` regenerated pre-pilot, baseline, and failure replay artifacts; `.venv/bin/python -m pytest tests/eval/test_pre_pilot_replay.py tests/unit/test_pre_pilot_docs.py tests/eval/test_demo_replay.py tests/unit/test_market_docs.py tests/eval/test_agent_eval.py tests/eval/test_tool_eval.py --tb=short` -> 37 passed; `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` -> 265 passed, 26 skipped; `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed; `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` -> passed.
- Follow-ups: collect external expert review using `docs/market/expert_review_rubric.md`; do not resume T67 until a human supplies or approves de-identified real pilot artifacts.
- Notes for next agent: pre-pilot evidence may be used for founder-led buyer conversations and shadow-mode pilot asks, but must not be used to claim production ROI, conversion lift, live-client proof, autonomous-send safety, or paid production readiness.

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
