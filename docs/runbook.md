# Operator Runbook

## Setup

1. Provision a T1 container runtime with the API, worker, PostgreSQL, and Redis services from `compose.yml`.
2. Set every runtime variable from deployment environment or secret storage.
3. Run `docker compose config` before deployment.
4. Run `python -m pytest tests/ -q --tb=short` before promoting a build.

## Webhook Configuration

Configure the inbound provider webhook URL as `/webhooks/inbound`. Set `WEBHOOK_SHARED_SECRET` in secret storage and configure the provider to sign request bodies with the matching HMAC SHA-256 signature.

## Seed Knowledge Ingestion

Load tenant-approved text FAQ, pricing, service-area, booking, cancellation, and escalation documents through the ingestion pipeline. Keep source documents canonical so the vector/index rows can be rebuilt when the embedding model or index schema changes.

## Operator Review

Operators use the JSON operator API to list human-review tasks, inspect transcript references, review evidence IDs, approve or edit proposed replies, and apply outcome labels. Unsafe message categories and unsupported retrieval results must stay in the review queue until an operator approves the final action.

## Rollback

Rollback application containers to the previous image. Database migrations must be forward-only or have an explicit rollback note before deployment. Preserve PostgreSQL data and Redis can be treated as ephemeral queue/cache state.

## Backup And Restore

Backup schedule: take a PostgreSQL custom-format backup before every production migration and at least once per day during the pilot. Store backups in deployment-managed storage with access limited to operators who already have production database access.

Backup command:

```bash
DATABASE_URL=postgresql://user:password@host:5432/lead_sla BACKUP_PATH=backups/lead_sla.dump ./scripts/backup_postgres.sh
```

Restore command:

```bash
DATABASE_URL=postgresql://user:password@host:5432/lead_sla_restore BACKUP_PATH=backups/lead_sla.dump VERIFY_COMMAND=".venv/bin/python -m pytest tests/integration/test_health.py -q --tb=short" ./scripts/restore_postgres.sh
```

Restore verification checklist:

- Restore into a non-production database first.
- Run the restore command with `VERIFY_COMMAND` set to a core smoke test.
- Confirm `/health` returns `{"status": "ok"}` for the restored environment.
- Confirm tenant-scoped repository tests pass before any restored database is promoted.
- Keep Redis empty after restore; it is ephemeral queue and timer state.

Local restore drill: create or obtain a fixture dump, restore it into a disposable local PostgreSQL database, then run the restore command with `VERIFY_COMMAND=".venv/bin/python -m pytest tests/integration/test_health.py tests/integration/test_persistent_repositories.py -q --tb=short"`.

Migration safety: every migration file must include a `downgrade()` function with rollback steps or an explicit irreversible rationale in the migration docstring. Run `ruff check alembic` and the full test suite before applying migrations. Take a backup immediately before migration and keep the previous application image available until post-migration smoke tests pass.

## Safe Handoff

Create a human-review task for unsupported evidence, stale evidence, provider failure, unsafe message categories, budget exhaustion, angry customers, high-value leads, and booking requests without explicit customer acceptance.

## Data Retention, Export, and Delete

Default pilot retention is 90 days unless the tenant contract sets a shorter value. Store the configured retention policy per tenant with `tenant_id`, `retain_days`, and `mode`. The only v1 delete mode is `anonymize`, which preserves operational counts and audit history while removing direct customer identifiers.

Tenant export schema version: `tenant-export-v1`

Tenant export includes:

- `leads`
- `conversations`
- `transcripts`
- `audit_events`
- `outcomes`
- `review_tasks`
- `retention_policy`
- `pii_fields`

PII fields identified in the export schema:

| Entity | PII fields |
|--------|------------|
| `leads` | `contact_name`, `contact_email`, `contact_phone` |
| `transcripts` | `provider_message_id` |
| `audit_events` | `event_metadata` may contain hashed identifiers or redacted previews |
| `review_tasks` | `payload` may contain lead/contact context and must be scrubbed on anonymization |

Delete/anonymize procedure:

1. Verify the requester is authorized for the tenant.
2. Export tenant data first if the contract or customer request requires a copy.
3. Run the tenant anonymization operation with actor ID and reason code.
4. Confirm lead contact fields are redacted, transcript provider IDs are removed, and review payloads are scrubbed.
5. Confirm an audit event named `tenant_data_anonymized` records actor ID, timestamp, reason, retention policy, and affected row counts.
6. Keep aggregate metrics and anonymized audit records for operational reporting unless the customer contract requires full deletion.

## Incident Response

All incident notes must use PII-free identifiers: tenant hash, provider, channel, queue name, corpus version, and failure reason. Do not paste lead IDs, phone numbers, emails, message text, provider message IDs, or transcript text into incident notes.

### Provider Outage

Signals: `provider_send_failure_total` above 2 percent of sends for 10 minutes, provider timeout errors, or failed send retry exhaustion.

Response:

1. Confirm `/health` and queue depth.
2. Check whether the outage is isolated to email, calendar, CRM, or embedding provider.
3. Pause unsafe autonomous sends for the affected provider and route new side effects to human review.
4. Retry failed jobs only after provider status recovers.
5. Record provider, failure reason, time window, and affected tenant hash.

### Retrieval Regression

Signals: `retrieval_freshness_age_hours` over 24 hours, `retrieval_latency_ms` p95 over 3000 ms, or `insufficient_evidence_total` over 20 percent of inbound leads for 30 minutes.

Response:

1. Freeze knowledge uploads for the affected tenant.
2. Run retrieval evals for seed, pilot, and vertical fixtures.
3. Check corpus version, embedding model, index schema version, and last reindex timestamp.
4. If quality regressed, route unsupported answers to human review until the eval passes.
5. Record corpus version, eval source, and regression classification.

### Queue Backlog

Signals: `queue_depth` greater than 100 pending jobs or growing for 15 minutes, SLA breaches increasing, or worker health degraded.

Response:

1. Check Redis connectivity and worker logs.
2. Scale worker replicas if provider rate limits are not the bottleneck.
3. Stop non-critical reindex or retry jobs before customer-response jobs.
4. Route leads that exceed SLA to human review.
5. Record queue name, depth, oldest job age, and mitigation.

### Webhook Signature Failures

Signals: repeated invalid signature responses, sudden drop in accepted provider events, or provider dashboard delivery errors.

Response:

1. Confirm the provider is sending the expected signature header.
2. Verify the active `WEBHOOK_SHARED_SECRET` for the environment without pasting it into logs.
3. Check whether a recent rotation changed only one side of the provider configuration.
4. Re-run a signed webhook smoke test.
5. Record provider, environment, failure count, and rotation status.

## Secrets

Real provider tokens, API keys, passwords, and webhook secrets must come from environment variables or deployment secret storage. Do not commit real credentials, `.env` files, provider tokens, or customer secrets to the repository.

### Environment Partitions

Use separate secret namespaces for each environment:

| Environment | Source | Rule |
|-------------|--------|------|
| Local | developer shell or local secret manager | Use test-only values; never paste production tokens into local `.env` files. |
| Staging | deployment secret store scoped to staging | Use staging provider accounts and staging databases only. |
| Production | deployment secret store scoped to production | Production tokens are readable only by the production runtime and the deployment operator rotating them. |

Do not share provider credentials between local, staging, and production. A staging failure must not affect production providers, production leads, production indexes, or production auth tokens.

### Secret Inventory

| Secret | Runtime recipient | Source |
|--------|-------------------|--------|
| `DATABASE_URL` | api, worker | Environment-specific PostgreSQL secret; never committed. |
| `REDIS_URL` | api, worker | Environment-specific Redis URL; no customer PII should be stored in Redis values. |
| `OPERATOR_AUTH_SECRET` | api only | Environment-specific operator-token signing secret. |
| `WEBHOOK_SHARED_SECRET` | api only | Provider webhook signing secret for inbound email, WhatsApp, Telegram, or website-form events. |
| `EMAIL_API_KEY`, `EMAIL_SENDER`, `EMAIL_API_URL` | worker only | Email provider account for outbound fallback sends. |
| `CALENDAR_API_TOKEN`, `CALENDAR_API_URL` | worker only | Calendar provider account used for slot lookup and booking. |
| `CRM_API_TOKEN`, `CRM_API_URL` | worker only | CRM or spreadsheet destination account for lead writes. |
| `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_API_URL` | worker only | Embedding provider account for indexing and retrieval. |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | postgres container only | Database bootstrap secrets used by Compose-managed PostgreSQL. |

### Runtime Scope

The API container receives only inbound/auth/database variables: `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_AUTH_SECRET`, and `WEBHOOK_SHARED_SECRET`.

The worker container receives only database/queue variables plus provider adapter credentials required for outbound messaging, calendar, CRM, embedding, and bounded worker configuration. The worker does not receive webhook signing or operator auth secrets.

### Rotation Procedure

1. Create the replacement secret in the target environment's secret store.
2. If the provider supports overlapping credentials, deploy the new secret while the old one remains valid.
3. Restart only the services that receive the rotated secret: API for webhook/operator auth, worker for provider adapters, PostgreSQL for bootstrap credentials only during controlled database maintenance.
4. Run `/health`, provider fake/contract smoke tests, and the operator auth smoke path.
5. Revoke the old provider token after the new deployment passes.
6. Record the rotation date, owner, affected environment, and smoke-test result in the deployment log.
