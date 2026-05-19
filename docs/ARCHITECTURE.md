# Architecture - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Status: Draft

---

## System Overview

Lead Response SLA Agent is an AI-assisted lead-response system for time-sensitive service businesses. It receives inbound leads from webhooks or messaging channels, sends a fast acknowledgement, qualifies the lead through a constrained conversation, grounds answers in an approved text knowledge base, books or proposes the next step through external tools, and escalates risky or high-value cases to a human operator. The system serves business owners, sales or operations managers, intake coordinators, and the AI engineer/operator maintaining the pilot workflow. It is a containerized FastAPI service with persistent state in PostgreSQL and bounded background workers for messaging, SLA timers, retrieval indexing, and provider retries.

---

## Problem Fit and Adoption Reality

### Problem-First Entry Gate

| Question | Answer |
|----------|--------|
| Concrete operational pain | Inbound leads arrive through forms, Telegram, WhatsApp, email, or landing pages, but human teams respond late, inconsistently, or without enough context. In urgent service categories, a delay of a few minutes can lose the lead to a competitor. |
| Current workaround | Manual inbox monitoring, CRM notifications, simple autoresponders, missed-call callbacks, template replies, and sales reps checking forms during business hours. |
| Why existing process is insufficient | Static autoresponders do not qualify the lead, cannot answer context-specific questions from approved knowledge, do not book a slot, and do not create structured CRM data. Fully manual response is slow and inconsistent. Unguarded chatbots can make unsafe promises about price, availability, policy, legal, or medical topics. |
| First user / operator who feels the pain | A small service business owner or operations lead in one time-sensitive pilot vertical, plus the AI engineer/operator configuring and monitoring the first workflow. |
| What would make v1 not worth adopting | Setup takes longer than a manual process improvement; the agent gives unsafe answers; the intake source cannot be connected; response latency does not improve; operators do not trust the transcript and audit trail. |
| First proof of value | p95 AI-assisted first-response latency below 30 seconds, deterministic acknowledgement under 2 seconds where possible, at least 80 percent of inbound leads captured as structured records, and improved booked calls or qualified handoffs versus the pre-pilot baseline. |

### Adoption Reality Gate

| Boundary | Decision |
|----------|----------|
| Work AI is expected to improve | Messy lead-message understanding, structured extraction, reply drafting, next-question selection inside a fixed policy, grounded FAQ answers, conversation summarization, and readiness-to-handoff scoring. |
| Work AI will not replace | Final sales judgment, pricing exceptions, refunds, legal/medical/financial advice, dispute handling, high-value commitments, and accountability for customer promises. |
| Claims not allowed before evidence | "Replaces sales reps", "fully autonomous closer", "guarantees conversion lift", "handles regulated advice", "production-ready for every vertical", and "zero-touch customer support". |
| Demo-to-production evidence required | Passing unit/integration tests, retrieval and tool-use evaluation baselines, conversation policy eval cases, operator review of transcripts, measured SLA latency, and real booked-call or qualified-handoff comparison against baseline. |

The project fits the playbook as a Standard governance overlay for a bounded AI workflow with external side effects, PII, active retrieval, and measurable production claims.

---

## Solution Shape

| Decision | Selection | Justification |
|----------|-----------|---------------|
| Primary shape | Hybrid: deterministic workflow orchestration plus a bounded conversational/tool-using agent | Intake validation, SLA timing, auth, idempotency, retries, audit, and hard escalation rules are deterministic. AI is used only where natural-language understanding and grounded reply drafting are needed. |
| Governance level | Standard | The product is customer-facing, touches PII, sends outbound messages, books customer-facing next steps, and needs eval/audit evidence, but v1 avoids regulated advice and privileged runtime mutation. |
| Runtime tier | T1 | A containerized service plus bounded workers is enough. There is no need for shell, package, or toolchain mutation at runtime, and no privileged long-lived autonomous worker. |

### Rejected Lower-Complexity Options

| Rejected option | Why it is insufficient |
|-----------------|------------------------|
| Deterministic-only | It cannot reliably interpret messy inbound messages, ask context-sensitive follow-up questions, or draft natural customer-facing replies across vertical-specific language without brittle rule explosion. |
| Workflow or human-in-the-loop assistant only | A pure workflow still leaves humans responding to every lead, which fails the first-response SLA that creates product value. Human approval remains for risky boundaries, but routine first response and qualification must be automated. |
| Simple tool use without planning / loops | Single-shot tool use is not enough for multi-turn qualification. The system needs a bounded conversation loop with explicit termination, budget, and handoff conditions. |
| Higher-autonomy agent | The task does not require open-ended planning, delegation, shell access, or mutable runtime behavior. A fixed conversation policy with bounded LLM decisions is safer and sufficient. |

### Minimum Viable Control Surface

- Webhook signature verification, idempotency keys, tenant/customer scoping, and duplicate lead detection.
- PII-safe logging, trace/span allowlists, and append-only message/audit events.
- Human approval gates for unsafe topics, custom commitments, non-standard pricing, and low-confidence responses.
- RAG `insufficient_evidence` path for unsupported knowledge-base answers.
- Tool schemas with side-effect classification, idempotency rules, retry policy, and unsafe-action confirmation.
- Agent loop termination rules, max-turn/max-cost budgets, and handoff reasons.
- CI gates for tests, lint, format, and profile-specific eval suites.

### Human Approval Boundaries

| Boundary | Human approval required? | Why |
|----------|--------------------------|-----|
| Non-standard pricing, discounts, refunds, custom contract terms | Yes | These create business commitments outside approved policy. |
| Legal, medical, financial, or regulated-domain advice | Yes | v1 avoids regulated advice; the agent must escalate instead of answering. |
| Angry customer, complaint, dispute, or high-value enterprise lead | Yes | Risk and relationship cost are higher than the value of automation. |
| Unsupported knowledge-base answer or low retrieval confidence | Yes | The system must not fabricate policy, availability, or price. |
| First acknowledgement, basic qualification, grounded FAQ answer, safe booking-slot suggestion | No, when policy and confidence gates pass | These are bounded, reversible, and measurable routine actions. |
| Calendar booking confirmation | Conditional | Slot suggestions can be automated; final booking is automated only when the calendar tool returns an available slot and the customer explicitly accepts it. |

### Deterministic vs LLM-Owned Subproblems

| Subproblem | Owner | Reason |
|------------|-------|--------|
| Webhook verification, authentication, RBAC, tenant scoping | Deterministic | Security boundaries must be testable and non-probabilistic. |
| Required-field validation, phone/email normalization, duplicate detection | Deterministic | These are formalizable transformations. |
| SLA timers, retries, provider rate limits, idempotency, audit triggers | Deterministic | Correctness depends on predictable state transitions. |
| Knowledge-base ingestion, chunking, index freshness checks | Deterministic | Retrieval corpus lifecycle must be repeatable and auditable. |
| Intent classification, field extraction from messy language, reply drafting | LLM, constrained by schema and policy | Natural-language variance is the core reason to use AI. |
| Next qualifying question selection | LLM inside a deterministic state machine | The LLM may choose among allowed next steps, but cannot invent policy states or side effects. |
| Answering business FAQ questions | LLM grounded by RAG | Answers must cite or trace to approved text evidence; unsupported questions return `insufficient_evidence` and escalate. |
| Booking and CRM writes | Deterministic tools called through guarded LLM/tool interface | Side effects are executed by tools with schema validation, idempotency, and unsafe-action gates. |

### Runtime and Isolation Model

| Property | Decision |
|----------|----------|
| Isolation boundary | T1 container boundary for API, worker, and optional scheduler containers. |
| Persistence model | PostgreSQL is canonical state; Redis is ephemeral queue/cache/timer state; retrieval index uses PostgreSQL plus pgvector unless replaced by ADR. |
| Network model | Egress only to configured messaging provider, calendar provider, CRM/spreadsheet provider, and LLM/embedding provider. |
| Secrets model | Secrets live in environment variables or deployment secret storage; workers receive only the provider tokens they need. |
| Runtime mutation boundary | Runtime must not install packages, mutate its toolchain, write code, or run shell-driven autonomous tasks. Dependency changes happen through code review and CI. |
| Rollback / recovery model | Deploy rollback reverts application containers; database migrations must be forward-only or have documented rollback; inbound events are idempotent; failed model/tool calls degrade to human handoff without losing transcripts. |

---

## Inference / Model Strategy

| Path / Task | Model class | Why this class | Fallback / escalation | Budget / latency constraint |
|-------------|-------------|----------------|-----------------------|-----------------------------|
| Lead intent classification and field extraction | Small/fast model with structured output | High volume, schema-bound, low tolerance for latency | Retry once; if schema validation fails, send safe acknowledgement and create human-review task | p95 below 3 seconds per model call during active conversation |
| Customer-facing reply drafting | Stable general model with tool/function calling and structured output | Needs policy-aware wording and safe tone for end users | Escalate to human when retrieval confidence is low, policy classifier flags risk, or cost/turn budget is exceeded | AI-assisted first response p95 below 30 seconds including provider send |
| Conversation summarization and handoff notes | Small/fast summarization model | Not latency-critical and can be corrected by operator | Fall back to transcript-only handoff if summary fails | Cost per lead tracked; no customer-facing dependency |
| Retrieval query rewrite, if needed | Small/fast model or deterministic normalization | Query rewrite may improve FAQ retrieval but must stay optional | Direct lexical/vector query if rewrite fails | Retrieval path p95 below 2 seconds before generation |

Rules:
- Webhook verification, auth, SLA timers, retries, provider rate limits, and hard escalation policies use no model.
- Model classes are chosen per workload and can be changed only with eval evidence and a decision-log update.
- Customer-facing preview models are not allowed in v1 unless an ADR documents risk, fallback, and eval acceptance.

---

## Capability Profiles

| Profile | Status | Evaluation Artifact | Justification |
|---------|--------|---------------------|---------------|
| RAG | ON | `docs/retrieval_eval.md` | The agent must answer from approved, frequently changing business knowledge such as FAQs, pricing ranges, service areas, availability rules, and escalation instructions. Retrieval must be text-only in v1 with an explicit `insufficient_evidence` path. |
| Tool-Use | ON | `docs/tool_eval.md` | The LLM may request side-effecting actions through registered tools: CRM lead creation/update, messaging sends, calendar slot lookup/booking, lead-history lookup, and human-review task creation. Tool contracts, idempotency, and unsafe-action gates govern these calls. |
| Agentic | ON | `docs/agent_eval.md` | The conversation runtime is a bounded observe-decide-act loop over customer messages and tool results. It is not higher autonomy; it is constrained by a deterministic state machine, turn budget, tool permissions, and termination/handoff conditions. |
| Planning | OFF | `docs/plan_eval.md` | The application does not produce structured plans as its primary deliverable. Development planning remains in the playbook workflow, not application runtime behavior. |
| Compliance | OFF | `docs/compliance_eval.md` | v1 handles PII and needs strong privacy controls, but no named regulatory framework is a launch gate. Regulated advice is explicitly out of scope. |

### Active Profile Justifications

RAG, Tool-Use, and Agentic are ON because they govern real runtime behavior in the first viable product. Retrieval owns approved knowledge grounding; Tool-Use owns external side effects; Agentic owns bounded multi-turn conversation control. Planning and Compliance stay OFF to avoid implying a structured-planning product or a named compliance launch gate before evidence exists.

### Profile: RAG

Reference: use `docs/RAG_REFERENCE.md`, based on https://github.com/ashishki/Dream_Motif_Interpreter, as a design reference for connector contracts, normalized document flow, pgvector/HNSW indexing, hybrid vector+FTS retrieval, exact recall, typed insufficient-evidence results, and retrieval eval discipline. It is reference material only; tenant isolation, PII policy, and lead-response domain constraints in this repository override it.

#### RAG Architecture

**Ingestion pipeline** (offline / scheduled):

```text
extract -> normalize -> chunk -> embed -> index
```

| Stage | Description | Technology |
|-------|-------------|------------|
| Extract | Fetch tenant-approved text sources: FAQ documents, price sheets, policy pages, service-area rules, and escalation instructions. | Admin upload/API import in FastAPI; local file loader for seed data. |
| Normalize | Convert markdown, plain text, CSV-like policy tables, and simple HTML into normalized text sections with metadata. | Python normalization module with Pydantic metadata schema. |
| Chunk | Split by document section and policy heading, keeping source title, effective date, tenant, and vertical metadata. | Custom chunker with deterministic tests. |
| Embed | Create embeddings for normalized text chunks. | Provider adapter behind `EmbeddingClient`; default stable text embedding model selected during implementation. |
| Index | Store chunk metadata and vector representation. | PostgreSQL plus pgvector for v1 unless ADR replaces it. |

**Query-time pipeline** (online / per request):

```text
query analyze -> retrieve -> filter -> assemble evidence -> answer | insufficient_evidence
```

| Stage | Description | Technology |
|-------|-------------|------------|
| Query analyze | Normalize customer question, infer allowed topic, and optionally rewrite for retrieval. | Deterministic normalization plus optional small-model rewrite. |
| Retrieve | Tenant-scoped vector search with metadata filters, plus optional PostgreSQL FTS candidate retrieval fused with vector candidates when eval proves it improves recall. | pgvector query through parameterized SQLAlchemy; FTS/RRF pattern may follow `docs/RAG_REFERENCE.md`. |
| Filter | Drop stale, wrong-tenant, wrong-vertical, or low-score chunks. | Deterministic score and metadata checks. |
| Assemble evidence | Build numbered evidence snippets for the reply drafter. | XML-like evidence envelope with source IDs. |
| Answer / insufficient_evidence | Draft an answer only when evidence meets coverage threshold; otherwise return `insufficient_evidence` and create handoff. | Reply policy service plus LLM structured output. |

#### Corpus Description

| Property | Value |
|----------|-------|
| Source documents | FAQs, pricing ranges, service descriptions, service-area rules, cancellation policies, booking rules, and escalation instructions approved by the operator. |
| Update frequency | Daily or ad hoc per operator update; v1 max index age is 24 hours. |
| Estimated size | Pilot corpus starts under 100 documents and under 10,000 chunks; design should tolerate thousands of chunks without redesign. |
| Access control | Tenant/customer corpus isolation by metadata filter and database tenant context; no cross-tenant retrieval. |

#### Retrieval / Embedding Strategy

| Decision | Selection | Why |
|----------|-----------|-----|
| Retrieval mode | text-only | v1 sources are FAQs, policies, price sheets, and booking rules. Images or multimodal evidence are not needed to answer first-response questions. |
| Modalities in scope | text only | Later screenshots, documents, or photos are explicitly out of scope for v1. |
| Text-only baseline considered? | yes | It is the minimum sufficient mode and keeps latency, eval burden, and index design manageable. |
| Embedding provider / model | Stable text embedding provider selected behind an adapter | The concrete model can change by ADR, but the index schema version and dimensions must be explicit once implemented. |
| Stability status | stable required for production | Preview embedding models are not allowed in v1 without ADR, fallback, and re-index plan. |
| Fallback / migration path | Keep source text canonical; re-index from source documents when embedding model or schema changes | Prevents locked-in stale vector state. |

#### Index Strategy

- Embedding model: stable text embedding model selected in implementation task T09 and recorded in `docs/retrieval_eval.md`.
- Chunking: heading/section-aware chunks with deterministic metadata; target chunk size and overlap recorded in T09. Prefer token-aware chunking once the embedding model/tokenizer is selected.
- Vector dimensions / representation contract: recorded in index schema version `rag-index-v1` after the provider is selected.
- Index schema version: `rag-index-v1`; changes require ADR and full re-index.
- Index implementation: PostgreSQL + pgvector by default; add an HNSW cosine index when corpus size or latency evidence justifies it.
- Exact recall: add deterministic FTS/exact-match retrieval for concrete business terms that must not be hidden by vector thresholds.
- Max index age: 24 hours for active tenant corpora.
- Evaluation plan: seed at least 10 representative queries covering pricing, service area, booking, cancellation, unsupported topic, stale/unknown policy, and tenant-isolation cases; track hit@3, hit@5, MRR, citation precision, no-answer accuracy, and retrieval latency.

#### Risks

| Risk | Mitigation |
|------|------------|
| Hallucination on weak evidence | Required `insufficient_evidence` path and explicit tests for unsupported questions. |
| Schema drift | Version chunk metadata and embedding model; ADR plus full re-index for schema changes. |
| Stale index | Health endpoint exposes corpus freshness; stale index produces warning and disables autonomous FAQ answers after threshold. |
| Corpus isolation failure | Tenant metadata filters and database tenant context; cross-tenant retrieval is automatic P1. |
| Retrieval latency regression | Track retrieval p95 in `docs/retrieval_eval.md` and CI eval suite. |
| Multimodal overreach | Multimodal retrieval is out of scope for v1 and requires ADR plus text baseline comparison. |
| Preview model instability | Production embedding model must be stable; preview requires explicit fallback and re-index plan. |

### Profile: Tool-Use

#### Tool Catalog

| Tool | Side effect | Unsafe? | Idempotency key | Human gate |
|------|-------------|---------|-----------------|------------|
| `send_message` | Sends outbound Telegram/WhatsApp/email message | Yes when message contains pricing, custom commitment, regulated topic, or low-confidence text | `conversation_id:message_hash:channel` | Required for unsafe categories; otherwise policy-gated automation allowed |
| `create_or_update_lead` | Creates or updates CRM/spreadsheet lead record | Write | `source_event_id` or `lead_id` | No, when schema validation passes |
| `lookup_available_slots` | Reads calendar availability | Read | n/a | No |
| `book_slot` | Creates calendar booking | Write | `lead_id:slot_id` | Requires explicit customer acceptance and policy eligibility |
| `lookup_lead_history` | Reads prior lead/conversation data | Read | n/a | No, but caller must be tenant-scoped |
| `create_human_review_task` | Creates operator queue item | Write | `conversation_id:handoff_reason` | No; this is the safe fallback |

Tool schemas are versioned from `tool-schema-v1`. Any schema change requires a task, tests, and a `docs/tool_eval.md` update.

### Profile: Agentic

#### Conversation Loop Contract

The runtime loop is: receive inbound event -> load conversation state -> classify/extract -> retrieve evidence if needed -> choose one allowed next action -> validate policy/tool request -> execute deterministic tool or enqueue human review -> append audit event -> terminate turn. The loop never runs unbounded: each lead has max turns, max tool calls per turn, max model budget, explicit handoff reasons, and a terminal status.

| Boundary | Rule |
|----------|------|
| Max autonomous turns | Configured per tenant; v1 default 6 customer-agent turns before handoff. |
| Max tool calls per turn | v1 default 3, excluding audit append. |
| Termination reasons | booked, qualified_handoff, human_review_required, unsupported_question, no_response_timeout, budget_exceeded, provider_error. |
| Memory | Conversation state comes from PostgreSQL transcript and structured lead fields, not hidden model memory. |
| Delegation | No subagents in runtime v1. |

---

## Component Table

| Component | File / Directory | Responsibility |
|-----------|------------------|----------------|
| API service | `src/lead_sla_agent/api/` | FastAPI app, health endpoint, auth, inbound webhooks, operator API. |
| Config | `src/lead_sla_agent/config.py` | Settings from environment, feature flags, provider credentials. |
| Database layer | `src/lead_sla_agent/db/` | SQLAlchemy models, migrations, tenant context, repositories. |
| Lead intake | `src/lead_sla_agent/intake/` | Webhook verification, event normalization, duplicate detection, lead creation. |
| Conversation runtime | `src/lead_sla_agent/conversation/` | State machine, policy gates, next-action loop, handoff decisions. |
| RAG ingestion | `src/lead_sla_agent/retrieval/ingestion.py` | Normalize, chunk, embed, and index approved knowledge documents. |
| RAG query | `src/lead_sla_agent/retrieval/query.py` | Tenant-scoped retrieval, evidence assembly, insufficient-evidence path. |
| Tool layer | `src/lead_sla_agent/tools/` | Versioned schemas and adapters for messaging, calendar, CRM, review queue. |
| Workers | `src/lead_sla_agent/workers/` | Queue consumers for outbound sends, SLA timers, retries, indexing jobs. |
| Observability | `src/lead_sla_agent/observability/` | Shared tracing, metrics, PII scrubbers, health reporting. |
| Evaluation | `tests/eval/` | Retrieval, tool-use, and agent loop regression checks. |
| Operator UI/API | `src/lead_sla_agent/operator/` | Review queue, transcripts, overrides, feedback labels. |

---

## Data Flow

1. A lead arrives through a signed webhook or configured messaging provider event.
2. The intake service verifies the signature, derives an idempotency key, normalizes the event, and stores an append-only inbound event.
3. The lead service creates or updates a structured lead record with tenant/customer scope.
4. The conversation runtime loads current state and decides whether a deterministic acknowledgement can be sent immediately.
5. For messy text, the model extracts intent and missing fields into a strict schema.
6. If the customer asks a business-policy question, the retrieval service fetches tenant-scoped text evidence and either returns evidence or `insufficient_evidence`.
7. The reply drafter chooses one allowed next action: ask a qualifying question, answer with evidence, propose a slot, create/update a lead, book a slot after explicit acceptance, or escalate.
8. The tool layer validates schema, side-effect class, idempotency key, and unsafe-action gate before executing external calls.
9. The system appends outbound messages, tool results, retrieved evidence IDs, model outputs, and policy decisions to the audit trail.
10. Operators review transcripts, approve or correct escalations, tag outcomes, and feed real failure cases into eval fixtures.

---

## Tech Stack

| Component | Technology choice | Rationale |
|-----------|-------------------|-----------|
| Language | Python 3.12 | Strong FastAPI/Pydantic ecosystem and clear async support. |
| API | FastAPI | Async webhooks, typed request/response models, OpenAPI docs, straightforward testing. |
| Validation | Pydantic v2 | Strict schemas for lead fields, tool calls, model outputs, and settings. |
| Database | PostgreSQL 16 | Durable lead, transcript, audit, tenant, and eval state. |
| Vector search | pgvector | Keeps v1 retrieval in PostgreSQL and avoids an extra vector service. |
| ORM / migrations | SQLAlchemy 2.x + Alembic | Parameterized SQL, async support, migration discipline. |
| Queue/cache | Redis 7 with `redis.asyncio` | SLA timers, retry queues, provider send jobs, lightweight locks. |
| Testing | pytest, pytest-asyncio, httpx | Async service tests and FastAPI client coverage. |
| Lint/format | Ruff | Fast lint and formatting in local and CI paths. |
| Observability | OpenTelemetry-compatible tracing plus structured logging | Required for external calls, model calls, retrieval latency, and tool-call audit. |
| Deployment | Docker Compose for v1 | One API container, one worker container, PostgreSQL, Redis; simple VPS deployment. |

---

## Security Boundaries

- Operator endpoints require authentication and role checks before accessing tenant or lead data.
- Public inbound webhooks must verify provider signatures before writing state.
- Tenant-scoped database access must set tenant context before querying tenant-owned tables.
- PII fields include name, phone, email, chat content, booking details, transcript text, lead notes, and provider identifiers.
- PII must not appear in logs, span attributes, metrics labels, returned error details, or CI artifacts.
- Secrets are read only from environment variables or deployment secret storage.
- Cross-tenant retrieval, transcript access, or CRM writes are automatic P1 violations.
- Calendar booking and outbound messaging are side effects; unsafe categories require human approval before execution.

---

## External Integrations

| Service | Purpose | Credential / Config |
|---------|---------|---------------------|
| Telegram Bot API | Pilot inbound/outbound messaging channel | `TELEGRAM_BOT_TOKEN`, webhook secret |
| WhatsApp provider, Twilio or 360dialog | Optional v1 messaging channel | Provider token, account ID, webhook secret |
| Email provider | Optional fallback outbound channel | API key and sender identity |
| Google Calendar or Calendly | Slot lookup and booking | OAuth/client credentials or API token |
| CRM/spreadsheet target, e.g. HubSpot, Airtable, Google Sheets | Lead record write destination | API token and destination IDs |
| LLM provider | Extraction, reply drafting, summaries, optional query rewrite | API key, model names, budget limits |
| Embedding provider | Text embeddings for approved knowledge base | API key, embedding model name |

---

## File Layout

```text
.
|--- .github/workflows/ci.yml
|--- docs/
|   |--- ARCHITECTURE.md
|   |--- CODEX_PROMPT.md
|   |--- DECISION_LOG.md
|   |--- EVIDENCE_INDEX.md
|   |--- IMPLEMENTATION_CONTRACT.md
|   |--- IMPLEMENTATION_JOURNAL.md
|   |--- agent_eval.md
|   |--- nfr.md
|   |--- retrieval_eval.md
|   |--- spec.md
|   |--- tasks.md
|   `--- tool_eval.md
|--- src/lead_sla_agent/
|   |--- api/
|   |--- conversation/
|   |--- db/
|   |--- intake/
|   |--- observability/
|   |--- operator/
|   |--- retrieval/
|   |--- tools/
|   `--- workers/
|--- tests/
|   |--- eval/
|   |--- integration/
|   `--- unit/
|--- alembic/
|--- pyproject.toml
|--- requirements.txt
`--- requirements-dev.txt
```

---

## Runtime Contract

| Variable | Description | Example value |
|----------|-------------|---------------|
| `APP_ENV` | Runtime environment | `local`, `staging`, `production` |
| `DATABASE_URL` | PostgreSQL async connection URL | `postgresql+asyncpg://lead:test@localhost:5432/lead_sla` |
| `REDIS_URL` | Redis URL for queues/timers | `redis://localhost:6379/0` |
| `SECRET_KEY` | Application signing secret | `test-secret-key` |
| `WEBHOOK_SHARED_SECRET` | Shared secret for test webhook verification | `test-webhook-secret` |
| `LLM_API_KEY` | LLM provider key | `test-llm-key` |
| `LLM_MODEL_FAST` | Model for extraction/classification | `stable-fast-model` |
| `LLM_MODEL_REPLY` | Model for customer-facing drafting | `stable-reply-model` |
| `EMBEDDING_API_KEY` | Embedding provider key | `test-embedding-key` |
| `EMBEDDING_MODEL` | Text embedding model | `stable-text-embedding` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token when Telegram channel is enabled | `test-telegram-token` |
| `WHATSAPP_PROVIDER_TOKEN` | WhatsApp provider token when enabled | `test-whatsapp-token` |
| `EMAIL_API_KEY` | Email provider API key when email fallback is enabled | `test-email-key` |
| `EMAIL_SENDER` | Verified sender identity for email fallback | `leads@example.test` |
| `CALENDAR_API_TOKEN` | Calendar provider token | `test-calendar-token` |
| `CRM_API_TOKEN` | CRM/spreadsheet provider token | `test-crm-token` |
| `MAX_AUTONOMOUS_TURNS` | Agent loop turn budget | `6` |
| `MAX_TOOL_CALLS_PER_TURN` | Tool-call budget for each inbound customer turn | `3` |
| `MAX_INDEX_AGE_HOURS` | Retrieval freshness threshold | `24` |

---

## Observability

- Every database, Redis, HTTP provider, LLM, embedding, retrieval, and tool call is wrapped in a shared tracing module at `src/lead_sla_agent/observability/tracing.py`.
- Metrics include external-call success/error counters, latency histograms, first-response latency, SLA breach rate, failed send rate, retrieval latency, insufficient-evidence rate, tool-call success rate, and agent termination reason counts.
- `GET /health` returns `{"status": "ok"}` when core dependencies are reachable and reports retrieval index freshness without leaking PII.
- Logs are structured and PII-scrubbed before emission.

---

## Continuity and Retrieval Model

- Canonical truth: `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_CONTRACT.md`, `docs/spec.md`, `docs/tasks.md`, `docs/CODEX_PROMPT.md`, ADRs, eval artifacts, tests, code, and review reports.
- Retrieval convenience: `docs/DECISION_LOG.md`, `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`, and task `Context-Refs`.
- Execution model: Codex-only direct execution. There is no Claude runtime and no `codex exec` invocation from inside Codex in the active workflow.
- Scoped retrieval is mandatory before changing architecture, runtime tier, auth, tenant boundaries, PII policy, retrieval semantics, tool side effects, agent loop rules, open findings, or heavy-task evidence.
- Journal notes are not proof when a test, eval, or audit report exists.

---

## Non-Goals

- Do not build a multi-vertical marketplace in v1.
- Do not claim to replace sales reps or close deals autonomously.
- Do not automate legal, medical, or financial advice.
- Do not add voice calls, payments, complex CRM automation, or outbound cold outreach in v1.
- Do not introduce a T2/T3 isolated or privileged runtime without a concrete mutation/isolation need and ADR.
- Do not enable multimodal retrieval for future flexibility.
- Do not build a generic contact center platform before the first vertical proves latency and conversion value.
