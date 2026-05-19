# Implementation Contract - Lead Response SLA Agent

Status: IMMUTABLE - changes require an ADR filed in `docs/adr/`
Version: 1.0
Effective date: 2026-05-19

Any agent may cite this document as the authority on implementation rules. Any implementation that violates this contract is a P1 finding unless a more severe classification is stated.

Execution model: Codex-only. There is no Claude Code runtime for this project, and active Codex sessions must not invoke Codex through `codex exec` or any nested Codex CLI call. Codex performs task implementation directly in the current workspace.

---

## Universal Rules

### SQL Safety

- All SQL is parameterized. Use `text()` with named parameters, for example `text("SELECT ... WHERE id = :id")` with `{"id": value}`.
- Never interpolate variables into SQL strings. This includes f-strings, percent formatting, and string concatenation.
- Never use string concatenation to build any part of a query, including table names, column names, or `ORDER BY` clauses.
- Violation: automatic P1.

### Multi-Tenant Systems

- Every database call that touches tenant-scoped tables must be preceded by transaction-scoped tenant context, preferably `SET LOCAL app.tenant_id = :tid`.
- No query executes against tenant-scoped tables without a tenant context.
- Session-level `SET` without `LOCAL` is forbidden in multi-tenant code paths because it can leak tenant context across requests.
- RLS policies must enforce tenant boundaries once migrations introduce tenant-scoped tables.
- Violation: automatic P1.

### Async Redis

- Redis is accessed only in `async def` functions.
- Use `redis.asyncio`, not the synchronous `redis` client.
- Never call synchronous Redis methods from async code paths.
- Violation: automatic P1.

### Authorization

- Every new route handler enforces authorization before accessing data unless it is explicitly public.
- Public webhook routes are allowed only when they verify the provider signature before writing state.
- Operator APIs must authenticate the caller and verify tenant/role authorization before returning lead, transcript, or review data.
- "Add auth later" is not an acceptable deferral.
- Violation: automatic P1.

### PII Policy

- No PII in log messages, span attributes, metrics labels, metric values, returned error messages, CI artifacts, or test snapshots.
- Where identifiers must appear in observability data, use SHA-256 hashes or an equivalent one-way hash.
- Fields considered PII in this project: name, phone, email, chat content, booking details, transcript text, lead notes, provider user IDs, provider message IDs when they identify a person, and raw webhook payloads.
- Violation: automatic P1.

### Credentials and Secrets

- No credentials, API keys, tokens, passwords, or secrets in source code.
- No credentials in comments.
- No real credentials in test fixtures; use placeholder strings such as `test-llm-key`.
- All secrets come from environment variables or deployment secret storage.
- `.env` files must be ignored and never committed.
- Violation: automatic P1 and security incident.

### Shared Tracing Module

- One shared tracing module: `src/lead_sla_agent/observability/tracing.py` with a single `get_tracer()` function.
- All code that creates spans imports from this module.
- No inline noop span implementations in individual files.
- No copy-pasted tracer initialization in individual modules.
- Violation: P2, escalating to P1 at age cap.

### CI Gate

- CI must pass before any PR is merged.
- A PR with failing CI is never merged.
- CI flakiness is fixed before merge rather than bypassed.
- CI setup is a Phase 1 deliverable and must not be deferred.
- Violation: automatic P1.

### Observability

- Every external call, including database, Redis, HTTP provider, LLM, embedding, retrieval, and tool calls, must be wrapped in a span with trace ID and operation name.
- For each external call type, emit success/error counters and latency histograms.
- `GET /health` returns `{"status": "ok"}` with HTTP 200 when the system is healthy. It must not log PII, must not count toward rate limits, and must not require authentication.
- Profile-specific metrics are required when a profile is ON:
  - RAG: `insufficient_evidence` counter, retrieval latency, generation latency, index freshness.
  - Tool-Use: tool name, success/failure, latency, unsafe-gate decisions.
  - Agentic: loop iteration count, termination reason, handoff reason, budget exhaustion.
- Missing health endpoint behavior is P1. Missing profile-specific metrics are P2.

---

## Project-Specific Rules

### First-Response SLA Is a Product Contract

The system must record first-response latency for every processed inbound event. Any path that sends or declines to send a first response must store a machine-readable status and reason.

Violation: P1 if latency cannot be measured; P2 if optional dashboard aggregation is missing.

### Conversation Runtime Must Stay Bounded

The runtime agent may choose only from the allowed action set declared in `docs/ARCHITECTURE.md`: acknowledge, ask question, answer with evidence, propose slot, create/update lead, book accepted slot, or handoff. It must enforce max turns, max tool calls per turn, max model budget, and explicit termination reasons.

Violation: automatic P1.

### Unsupported Knowledge Must Escalate

If retrieval returns `insufficient_evidence`, stale evidence, cross-tenant evidence, or evidence below threshold, customer-facing answer drafting is forbidden. The system must create a human-review task.

Violation: automatic P1.

### External Writes Must Be Idempotent

Messaging sends, CRM writes, booking writes, and human-review task creation must use idempotency keys where technically feasible. Non-idempotent writes must be listed in the Tool Catalog with a justification before implementation.

Violation: P1 for missing idempotency on supported write tools; P2 for incomplete catalog metadata.

### Provider Credentials Are Adapter-Scoped

Provider adapters may read only the environment variables they require. Tests use fake adapters and placeholder values. Real provider tokens must not be required for unit or integration tests.

Violation: automatic P1 for real credential exposure; P2 for tests that require live provider credentials without explicit integration-test opt-in.

---

## Continuity and Retrieval Rules

- Canonical truth lives in `docs/ARCHITECTURE.md`, `docs/spec.md`, `docs/tasks.md`, `docs/CODEX_PROMPT.md`, this contract, ADRs, eval artifacts, tests, code, and review reports.
- Retrieval convenience lives in `docs/DECISION_LOG.md`, `docs/IMPLEMENTATION_JOURNAL.md`, `docs/EVIDENCE_INDEX.md`, and task `Context-Refs`.
- Read scoped continuity references before changing architecture, runtime tier, auth, tenant isolation, PII policy, retrieval semantics, tool side effects, agent loop rules, eval baselines, open findings, or any task marked `Execution-Mode: heavy`.
- Journal notes are never proof when a test, eval artifact, or review report exists.
- If a task changes a decision, update `docs/DECISION_LOG.md` and add an ADR when the change affects architecture, runtime tier, governance level, profile state, model strategy, retrieval mode, or immutable contract rules.

---

## Control Surface and Runtime Boundaries

| Boundary | Rule |
|----------|------|
| Secrets scope | API and worker containers receive only their required environment variables. Provider adapters read adapter-specific tokens only. |
| Network egress | Runtime egress is limited to configured LLM/embedding, messaging, calendar, CRM/spreadsheet, PostgreSQL, and Redis endpoints. |
| Privileged actions | Non-standard pricing, refunds, regulated advice, custom commitments, unsafe message sends, and booking without explicit customer acceptance require human approval or are forbidden. |
| Runtime mutation | Runtime must not install packages, mutate toolchains, write code, or run shell-driven autonomous tasks. |
| Persistence | PostgreSQL is canonical. Redis is ephemeral queue/timer/cache state. Retrieval source documents are canonical; vector index can be rebuilt. |
| Auditability | Inbound events, outbound sends, model outputs, retrieved evidence IDs, tool calls, human approvals, and termination reasons are appended to audit records. |

### Runtime Tier Guardrails

- Implement only within T1 container/bounded worker runtime.
- Runtime-tier expansion is a governance change requiring ADR and human approval.
- The project must not silently acquire T2/T3 behaviors such as privileged workers, broad shell mutation, snapshot-managed autonomous runtimes, or long-lived mutable runtime state.

---

## Mandatory Pre-Task Protocol

1. Read this contract.
2. Read the target task in `docs/tasks.md`.
3. Read the task's `Depends-On` summaries and `Context-Refs`.
4. If the task is heavy, changes risky boundaries, or has a profile trigger tag, read the matching eval artifact and decision log entries.
5. Do the task directly in the active Codex session; do not call `codex exec`.
6. Run `python -m pytest tests/ -q` to capture the current baseline after tests exist.
7. Run `ruff check src/lead_sla_agent tests` and `ruff format --check src/lead_sla_agent tests` after the project skeleton exists.
8. Do not write implementation code before understanding the acceptance criteria and required test functions.
9. Write or update tests for every acceptance criterion.
10. Update eval artifacts when a task has RAG, Tool-Use, or Agentic trigger tags.
11. Update `docs/CODEX_PROMPT.md` when baseline, next task, findings, or profile state changes.

---

## Forbidden Actions

| Action | Why Forbidden |
|--------|---------------|
| String interpolation or concatenation in SQL | SQL injection risk; parameterized queries are mandatory. |
| Session-level `SET` for tenant context | Tenant context can leak across requests; use transaction-scoped context. |
| Skipping pre-task baseline capture | Regressions cannot be detected. |
| Running tests without recording baseline impact | Test results lose their role as evidence. |
| Self-closing review findings without code verification | Findings close by inspecting evidence, not by assertion. |
| Modifying this contract without an ADR | The contract is immutable. |
| Deferring CI setup past Phase 1 | Every commit after Phase 1 must be CI-verifiable. |
| Merging with failing CI | The CI gate exists to prevent unverified changes. |
| Committing credentials or secrets | Credential exposure is irreversible. |
| Unauthorized runtime-tier expansion | T2/T3 behaviors require explicit architecture approval. |
| Calling `codex exec` from an active Codex session | This project is Codex-only and tasks run directly in the current workspace. |
| Customer-facing answer after `insufficient_evidence` | Unsupported answers create trust and liability risk. |
| Side-effecting tool call without required idempotency key | Duplicate provider actions can affect customers and CRM records. |

---

## Quality Process Rules

- P2 Age Cap: any P2 finding open for more than three review cycles must be resolved, escalated to P1, or formally deferred by ADR before the next phase gate.
- Retrieval-critical P2 findings have a one-cycle age cap.
- One logical change per commit. Do not bundle unrelated migrations, service logic, and review fixes.
- Commit messages use `type(scope): description`.
- No AI `Co-authored-by` trailers in commits.
- A Codex session that wrote a change may perform verification, but must not label that verification as independent review.
- Independent review requires a fresh Codex session or human reviewer.
- Review passes do not write application code.

---

## RAG Rules

Applies because RAG Profile is ON.

- Retrieval mode is text-only in v1. Multimodal retrieval requires ADR, text baseline comparison, updated architecture, and updated retrieval eval.
- Ingestion and query-time retrieval live in separate modules.
- Corpus isolation is enforced at query time by tenant filtering and database tenant context.
- Cross-tenant retrieval is automatic P1.
- Every query-time path must support `insufficient_evidence`.
- Unsupported or stale evidence must create human review instead of customer-facing answer text.
- Index schema version is `rag-index-v1` until changed by ADR.
- Changing embedding model, vector dimensions, chunking strategy, metadata schema, retrieval mode, or corpus ACL requires ADR and full re-index.
- Maximum index age is 24 hours for active tenant corpora.
- Health checks expose retrieval freshness without PII.
- A retrieval task is not complete until `docs/retrieval_eval.md` is updated with current metrics and compared to baseline.
- Every retrieval eval history row must include Date, Eval Source, Corpus version, Dataset, Metrics, Root cause, Result, and Notes. Missing or vague Eval Source makes the evaluation invalid.
- Retrieval quality and answer quality are separate gates. Green tests or good answer-quality scores do not close retrieval metric regressions.

---

## Tool-Use Rules

Applies because Tool-Use Profile is ON.

- Every tool schema is versioned and listed in the Tool Catalog.
- Tool metadata includes side-effect classification, idempotency rule, timeout, retry policy, and human-gate rule.
- Every external write must be idempotent where technically feasible.
- Unsafe or irreversible actions require an explicit confirmation or human-review path before execution.
- A tool that writes, modifies, deletes, sends, books, or creates external state without documented side effects is a P1 finding.
- Tool calls must be traced and audited with tool name, schema version, success/failure, latency, idempotency key hash, and side-effect class.
- A Tool-Use task is not complete until `docs/tool_eval.md` is updated with current results and baseline comparison.

---

## Agentic Rules

Applies because Agentic Profile is ON.

- The application agent is a bounded conversation loop, not a higher-autonomy executor.
- The loop may choose only declared allowed actions.
- The loop must enforce max turns, max tool calls per turn, max model budget, and explicit termination reasons.
- Runtime subagents, hidden model memory, shell execution, package installation, and toolchain mutation are forbidden in v1.
- Conversation state comes from PostgreSQL and transcript records, not unstated prompt memory.
- Every handoff includes reason, transcript references, evidence IDs when available, proposed reply when available, and required operator action.
- An Agentic task is not complete until `docs/agent_eval.md` is updated with current results and baseline comparison.

---

## Profile Evaluation Rules

- Active profile eval artifacts are `docs/retrieval_eval.md`, `docs/tool_eval.md`, and `docs/agent_eval.md`.
- Every active profile eval must define method, dataset/scenarios, baseline, regression criteria, current result, and open findings.
- A profile-trigger task is not complete until the matching eval artifact is updated.
- A regression against baseline is a P1 unless documented with justification and explicitly accepted by the human reviewer before phase gate.
- "Tests are green" does not satisfy profile evaluation.

---

## Governing Documents

| Document | Role | Mutability |
|----------|------|------------|
| `docs/ARCHITECTURE.md` | Architecture, solution shape, profiles, runtime, boundaries | Changes need decision log; significant changes need ADR |
| `docs/spec.md` | Product and feature acceptance criteria | Human-approved scope changes |
| `docs/tasks.md` | Task contracts and acceptance tests | Active tasks may change; completed tasks append-only except corrections |
| `docs/CODEX_PROMPT.md` | Current state and session handoff | Updated every phase boundary and state change |
| `docs/IMPLEMENTATION_CONTRACT.md` | Immutable implementation rules | ADR required |
| `docs/retrieval_eval.md` | RAG eval baseline and results | Updated on RAG tasks |
| `docs/tool_eval.md` | Tool-use eval baseline and results | Updated on Tool-Use tasks |
| `docs/agent_eval.md` | Agent loop eval baseline and results | Updated on Agentic tasks |
| `docs/DECISION_LOG.md` | Decision index | Updated on architecture or policy decisions |
| `docs/IMPLEMENTATION_JOURNAL.md` | Append-only continuity notes | Updated after tasks/sessions |
| `docs/EVIDENCE_INDEX.md` | Index of durable proof | Updated when evidence artifacts are added |
