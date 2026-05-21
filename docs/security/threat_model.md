# Threat Model - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-21
Scope: VPS pilot production boundary for webhooks, operator APIs, provider calls, tenant isolation, and bounded agent behavior.

---

## Assets

- Tenant data: leads, conversations, transcript hashes, review tasks, outcomes, tenant configuration, usage, and audit events.
- Secrets: webhook shared secret, operator auth secret, provider API tokens, database URL, Redis URL, Grafana credentials, deploy SSH key.
- Provider trust links: Postmark inbound/outbound email, Twilio WhatsApp, Telegram Bot API, calendar provider, CRM/spreadsheet destination.
- Operator actions: approve/send, no-send, knowledge upload, tenant configuration, outcome labels, support and incident records.
- Availability: public webhook intake, operator console APIs, worker queues, metrics endpoint, provider retry paths.
- Reputation and safety: no autonomous unsafe sends, no cross-tenant data exposure, no raw PII in logs/metrics/evals.

## Actors

- Legitimate lead: sends inbound messages through email, WhatsApp, or Telegram.
- Pilot operator or owner: authenticates with signed bearer token and reviews/approves actions.
- Provider platform: delivers webhooks and receives outbound API calls.
- External attacker: sends unsigned webhooks, brute-force traffic, replay attempts, prompt-injection payloads, or token guesses.
- Malicious or compromised operator: attempts cross-tenant access, dangerous config changes, or unauthorized data export.
- Infrastructure operator: deploys to VPS, manages secrets, backups, Grafana, and reverse proxy configuration.

## Trust Boundaries

- Internet to VPS reverse proxy: public traffic enters `/webhooks/inbound`, `/health`, and `/metrics`; operator endpoints must remain protected behind auth and network policy.
- Reverse proxy to FastAPI app: proxy must preserve method/body, enforce TLS, and avoid trusting client-supplied IP headers unless overwritten by the proxy.
- FastAPI app to PostgreSQL/Redis: every tenant-scoped repository call must require tenant ID and apply tenant context or RLS where available.
- FastAPI app/workers to providers: outbound calls must use provider-scoped credentials, idempotency keys, timeouts, and human approval gates for live sends.
- Agent runtime to customer-facing channels: model-like output is constrained by policy, retrieval evidence, allowed actions, max turns, and human handoff.
- Observability boundary: logs, metrics, alerts, eval artifacts, and support notes must remain PII-free or redacted.

## Top Threats And Controls

| Threat | Primary controls | Evidence |
|--------|------------------|----------|
| Unsigned or forged provider webhook | HMAC/provider-specific signature verification before normalization or persistence; generic 401 error; no raw payload persistence | `tests/integration/test_security_controls.py::test_webhook_signature_failure_writes_no_rows` |
| Provider replay inflates leads or review work | Tenant + source event ID idempotency key; replay returns existing IDs; derived workflow objects are not duplicated | `tests/integration/test_security_controls.py::test_webhook_replay_is_idempotent_across_workflow_objects` |
| Webhook flooding or brute-force signature attempts | Per-client in-process webhook limit: 60 requests per 60 seconds by default; 429 with `Retry-After`; no second write after limit | `tests/integration/test_security_controls.py::test_webhook_rate_limit_returns_429_without_second_write` |
| Operator API brute force or scraping | Signed bearer token auth, role allow-list, per-client operator limit: 120 requests per 60 seconds by default; 429 with `Retry-After` | `tests/integration/test_security_controls.py::test_operator_rate_limit_returns_429` |
| Cross-tenant operator data access | Tenant ID is inside signed token claims; review/outcome/knowledge stores filter by principal tenant; PostgreSQL repositories apply tenant context and RLS | `tests/integration/test_security_controls.py::test_operator_token_tenant_scope_filters_review_tasks`, `tests/integration/test_rls_tenant_isolation.py` |
| Prompt injection or instruction override | Deterministic marker gate routes injection-like messages to human review before qualification, retrieval, or customer draft; no outbound draft is returned | `tests/integration/test_security_controls.py::test_prompt_injection_routes_to_human_review_without_customer_draft`, `docs/agent_eval.md` |
| Unsafe autonomous provider send | Live messaging gateway requires human approval by default; unsafe categories create review tasks; provider results record rate-limit/failure status | `tests/integration/test_live_messaging_contract.py` |
| Provider duplicate or partial failure | Provider calls use idempotency keys where available; reconciliation detects missing, duplicate, failed, rate-limited, and stale provider records | `tests/integration/test_provider_reconciliation.py` |
| Raw PII leaks into logs, metrics, or eval artifacts | Structured redaction filters hash or redact emails, phones, names, addresses, messages, provider IDs, tokens, and secrets | `tests/integration/test_log_redaction.py`, `tests/unit/test_observability_contract.py` |
| Dangerous tenant configuration change | Unsupported fields rejected; dangerous changes require owner role or explicit approval ID; audit history is tenant scoped | `tests/integration/test_tenant_admin.py` |

## Rate-Limit Behavior

- Webhook intake: `/webhooks/inbound` allows 60 requests per 60 seconds per FastAPI-observed client host by default. When exceeded, the API returns HTTP 429 with body `{"detail":"rate limited"}` and a `Retry-After` header in seconds.
- Operator APIs: `/operator/*` and `/operator/knowledge/*` allow 120 requests per 60 seconds per FastAPI-observed client host by default. When exceeded, the API returns HTTP 429 with the same response shape.
- Current implementation is in-process and deterministic for the single-VPS pilot. It protects one app process, not a multi-process or multi-node cluster.
- Production reverse proxy configuration must ensure the app sees a stable client identity. Do not trust client-supplied `X-Forwarded-For` unless the VPS proxy overwrites it.
- Future scaling requirement: move counters to Redis before running multiple API workers or multiple VPS instances.

## Residual Risks

- The rate limiter is in-memory and resets on deploy/restart. This is acceptable for the first single-process VPS pilot, but it is not sufficient for horizontal scaling.
- Prompt-injection detection is a deterministic deny-list. It blocks common instruction-override attempts and fails closed to human review, but it does not replace broader adversarial evals.
- Provider signature verification currently uses the configured shared secret/test abstraction for provider-specific headers. Live provider onboarding must confirm exact vendor signing rules before accepting production traffic.
- `/metrics` is unauthenticated at the app layer for Prometheus scraping. VPS reverse proxy/firewall rules must restrict access if the endpoint is exposed beyond the monitoring path.
- Operator bearer tokens are signed and expirable, but there is no token revocation list yet. Short lifetimes and secret rotation remain required operational controls.

## Stop-Ship Security Findings

None open as of 2026-05-21.

Any P0/P1 security finding must be added to `docs/CODEX_PROMPT.md` Fix Queue and left there until resolved or explicitly accepted by the human owner.
