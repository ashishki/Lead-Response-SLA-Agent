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

## Safe Handoff

Create a human-review task for unsupported evidence, stale evidence, provider failure, unsafe message categories, budget exhaustion, angry customers, high-value leads, and booking requests without explicit customer acceptance.

## Secrets

Real provider tokens, API keys, passwords, and webhook secrets must come from environment variables or deployment secret storage. Do not commit real credentials, `.env` files, provider tokens, or customer secrets to the repository.
