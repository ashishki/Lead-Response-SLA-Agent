# Operator Runbook

## Setup

1. Provision a T1 container runtime with the API, worker, PostgreSQL, and Redis services from `compose.yml`.
2. Set every runtime variable from deployment environment or secret storage.
3. Run `docker compose config` before deployment.
4. Run `python -m pytest tests/ -q --tb=short` before promoting a build.

## Deployment Target

The first staging and production target is a VPS with Docker Compose, accepted in `docs/adr/ADR-004-deployment-target.md`. Runtime remains T1: bounded API and worker containers, PostgreSQL, Redis, environment-managed secrets, and no privileged autonomous runtime mutation.

Required resources:

| Environment | Resource | Owner | Backup | Retention | Cost Expectation |
|-------------|----------|-------|--------|-----------|------------------|
| staging | VPS with Docker Compose API, worker, PostgreSQL, Redis | founder/operator | nightly PostgreSQL dump before migration tests | 7 days | low fixed monthly VPS cost |
| production | VPS with Docker Compose API, worker, PostgreSQL, Redis | founder/operator | daily PostgreSQL dump and pre-migration dump | 30 days minimum during pilot | low fixed monthly VPS cost plus backup storage |
| staging | environment secret file on host | founder/operator | recreate from secret store; do not back up plaintext | rotate on exposure or staff change | included in VPS ops |
| production | environment secret file on host | founder/operator | recreate from secret store; do not back up plaintext | rotate on exposure or staff change | included in VPS ops |
| both | Docker container logs | founder/operator | export only for incidents after PII review | 14 days local retention | included in VPS disk budget |

Concrete staging deploy command:

```bash
ssh "$STAGING_VPS_USER@$STAGING_VPS_HOST" "cd /srv/lead-sla-agent && git fetch --prune && git checkout $GITHUB_SHA && docker compose config && docker compose up -d postgres redis && docker compose run --rm api alembic upgrade head && docker compose up -d --build api worker && docker compose ps"
```

Concrete production deploy command:

```bash
ssh "$PRODUCTION_VPS_USER@$PRODUCTION_VPS_HOST" "cd /srv/lead-sla-agent && BACKUP_PATH=backups/pre-migration-$GITHUB_SHA.dump ./scripts/backup_postgres.sh && git fetch --prune && git checkout $GITHUB_SHA && docker compose config && docker compose up -d postgres redis && docker compose run --rm api alembic upgrade head && docker compose up -d --build api worker && docker compose ps"
```

Concrete app rollback command:

```bash
ssh "$PRODUCTION_VPS_USER@$PRODUCTION_VPS_HOST" "cd /srv/lead-sla-agent && git checkout $ROLLBACK_GIT_SHA && docker compose up -d --build api worker && docker compose ps"
```

## Webhook Configuration

Configure the inbound provider webhook URL as `/webhooks/inbound`. Set `WEBHOOK_SHARED_SECRET` in secret storage and configure the provider to sign request bodies with the matching HMAC SHA-256 signature.

## Seed Knowledge Ingestion

Load tenant-approved text FAQ, pricing, service-area, booking, cancellation, and escalation documents through the ingestion pipeline. Keep source documents canonical so the vector/index rows can be rebuilt when the embedding model or index schema changes.

## Assisted Tenant Onboarding

Use the assisted onboarding checklist before launching a second tenant:

```bash
python scripts/onboard_tenant.py \
  --tenant-name "DFW Door Pilot" \
  --tenant-slug "dfw-door-pilot" \
  --operator-email "operator@example.test"
```

The checklist must fit within one working day and cover:

- tenant creation
- provider sandbox send/receive test
- approved knowledge upload
- operator account setup
- at least 10 tenant-specific knowledge questions
- operator approval path
- test lead validation

Launch gate: do not enable production traffic until provider sandbox passes, the 10-question knowledge validation passes, and an operator approves/edits/sends a test review task.

## Operator Review

Operators use the JSON operator API to list human-review tasks, inspect transcript references, review evidence IDs, approve or edit proposed replies, and apply outcome labels. Unsafe message categories and unsupported retrieval results must stay in the review queue until an operator approves the final action.

## Rollback

Rollback application containers to the previous image. Database migrations must be forward-only or have an explicit rollback note before deployment. Preserve PostgreSQL data and Redis can be treated as ephemeral queue/cache state.

Rollback decision path:

| Decision | Use when | Required proof |
| --- | --- | --- |
| App-only rollback | The release failed in application code, provider wiring, or configuration, and the database schema remains compatible with the previous image. | Previous image or `rollback_git_sha`, unchanged `alembic current`, and smoke tests after rollback. |
| Migration rollback | The failure is caused by the latest migration and that migration has downgrade coverage. | Recorded migration version before rollback, migration version after rollback, successful `alembic downgrade -1`, re-upgrade rehearsal, and smoke tests. |
| Restore from backup | Data is corrupted, a migration is irreversible, downgrade validation fails, or the database state is not trusted. | Pre-migration backup path, restore into non-production first, restore verification command, and post-restore smoke tests. |

Staging rollback rehearsal must record `migration_version_before`, `migration_version_after`, `rollback_decision`, `backup_path`, and `smoke_result` in `docs/rollback_rehearsal.md`. Validate the artifact and migration rollback coverage before production promotion:

```bash
python scripts/rollback_check.py --rehearsal-artifact docs/rollback_rehearsal.md
```

## Release Discipline

CI separates checks into unit tests, integration tests, eval gates, and deployment checks. A release cannot be promoted unless all four categories pass.

Staging promotion:

1. Deploy the candidate image to staging.
2. Run `alembic upgrade head` against the staging database.
3. Run staging smoke tests: `python scripts/smoke_test.py --environment staging --base-url https://staging.example.test --tenant-id smoke-staging --sandbox-mode`.
4. Fill out `docs/release_template.md`, including model, prompt, schema, and eval changes.
5. Verify rollback assets: previous image, PostgreSQL backup, restore command, and smoke tests.

Production promotion:

1. Promote only after staging migration and smoke tests pass.
2. Take a production PostgreSQL backup immediately before migration.
3. Run production migrations.
4. Run production smoke tests: `python scripts/smoke_test.py --environment production --base-url https://app.example.test --tenant-id smoke-production --sandbox-mode`.
5. Keep the previous application image available until post-release checks pass.

Smoke tests validate API health, Alembic migration version, Redis connectivity, operator auth, provider sandbox path, and unsafe-message handoff. The provider sandbox check is skipped unless `--sandbox-mode` is present; smoke tests must never send to real customer recipients.

Rollback validation:

1. Restore a recent backup into a non-production database.
2. Run `scripts/restore_postgres.sh` with `VERIFY_COMMAND` set to health and persistence smoke tests.
3. Confirm release notes identify the previous image and backup path.
4. Do not promote to production if rollback validation has not been completed for the release.
5. Confirm `docs/rollback_rehearsal.md` records the migration version before rollback and migration version after rollback.

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

## Audit Event Retention and Export

Canonical audit events are stored in PostgreSQL `audit_log_event` rows under tenant RLS. Search/export access is limited to owner or operator roles and must always apply tenant context before reading audit rows.

Audit payloads must contain operational references only: actor refs or hashes, action, resource type, resource ID/ref, result, policy version, timestamp, and PII-free metadata. Raw lead names, phone numbers, email addresses, transcripts, provider user IDs, bearer tokens, API keys, and webhook payloads are rejected before storage.

Retention defaults to the tenant retention policy, with a minimum pilot retention target of 90 days unless a signed customer agreement requires a longer period. Exports should be generated from tenant-scoped searches and reviewed for PII before sharing outside the operating team.

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

Local required secrets:

| Runtime | Secret names |
|---------|--------------|
| api | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_AUTH_SECRET`, `WEBHOOK_SHARED_SECRET` |
| worker | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `EMAIL_API_KEY`, `EMAIL_SENDER`, `EMAIL_API_URL`, `CALENDAR_API_TOKEN`, `CALENDAR_API_URL`, `CRM_API_TOKEN`, `CRM_API_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_API_URL`, `MAX_AUTONOMOUS_TURNS`, `MAX_TOOL_CALLS_PER_TURN`, `MAX_INDEX_AGE_HOURS` |

Staging required secrets:

| Runtime | Secret names |
|---------|--------------|
| api | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_AUTH_SECRET`, `WEBHOOK_SHARED_SECRET` |
| worker | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `EMAIL_API_KEY`, `EMAIL_SENDER`, `EMAIL_API_URL`, `CALENDAR_API_TOKEN`, `CALENDAR_API_URL`, `CRM_API_TOKEN`, `CRM_API_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_API_URL`, `MAX_AUTONOMOUS_TURNS`, `MAX_TOOL_CALLS_PER_TURN`, `MAX_INDEX_AGE_HOURS` |
| deploy workflow | `STAGING_VPS_HOST`, `STAGING_VPS_USER`, `STAGING_VPS_SSH_KEY` |

Production required secrets:

| Runtime | Secret names |
|---------|--------------|
| api | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_AUTH_SECRET`, `WEBHOOK_SHARED_SECRET` |
| worker | `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `EMAIL_API_KEY`, `EMAIL_SENDER`, `EMAIL_API_URL`, `CALENDAR_API_TOKEN`, `CALENDAR_API_URL`, `CRM_API_TOKEN`, `CRM_API_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_API_URL`, `MAX_AUTONOMOUS_TURNS`, `MAX_TOOL_CALLS_PER_TURN`, `MAX_INDEX_AGE_HOURS` |
| deploy workflow | `PRODUCTION_VPS_HOST`, `PRODUCTION_VPS_USER`, `PRODUCTION_VPS_SSH_KEY` |

Provider adapter scopes:

| Adapter | Worker-only secret names |
|---------|--------------------------|
| email | `EMAIL_API_KEY`, `EMAIL_SENDER`, `EMAIL_API_URL` |
| calendar | `CALENDAR_API_TOKEN`, `CALENDAR_API_URL` |
| crm | `CRM_API_TOKEN`, `CRM_API_URL` |
| embedding | `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_API_URL` |

Database bootstrap secrets `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` belong only to the PostgreSQL container or host provisioning process.

### Runtime Scope

The API container receives only inbound/auth/database variables: `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_AUTH_SECRET`, and `WEBHOOK_SHARED_SECRET`.

The worker container receives only database/queue variables plus provider adapter credentials required for outbound messaging, calendar, CRM, embedding, and bounded worker configuration. The worker does not receive webhook signing or operator auth secrets.

### Rotation Procedure

1. Create the replacement secret in the target environment's secret store.
2. If the provider supports overlapping credentials, deploy the new secret while the old one remains valid.
3. Restart only the services that receive the rotated secret: API for webhook/operator auth, worker for provider adapters, PostgreSQL for bootstrap credentials only during controlled database maintenance.
4. Run `/health`, provider fake/contract smoke tests, and the operator auth smoke path.
5. Revoke the old provider token after the new deployment passes.
6. Verify revocation by making a negative smoke call with the old credential and confirming it fails without logging the credential value.
7. Record the rotation date, owner, affected environment, revocation check, and smoke-test result in the deployment log.
