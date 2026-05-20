# ADR-004: Deployment Target

Date: 2026-05-20

## Status

Accepted

## Context

The first paid pilot needs a real staging and production environment for the API, worker, PostgreSQL, Redis, migrations, secrets, logs, metrics, backups, and rollback. The project is already designed as a T1 Docker Compose runtime with one API container, one worker container, PostgreSQL, and Redis.

The founder/operator selected a VPS because it is simpler and more understandable for the initial operations model. The priority for the first pilot is a deployment path the operator can inspect, repair, and back up directly.

## Decision

Use a VPS with Docker Compose as the first staging and production deployment target.

Runtime tier remains T1. The runtime is still bounded containers plus PostgreSQL and Redis. This decision does not introduce privileged workers, shell-driven autonomous runtime mutation, snapshot-managed runtimes, or any T2/T3 behavior.

Staging and production each use a separate VPS host and separate environment-specific secrets. The repository is deployed to `/srv/lead-sla-agent`, and the deployment workflow connects by SSH, checks out the target commit, validates `docker compose config`, starts PostgreSQL and Redis, runs Alembic migrations, starts API and worker containers, and runs smoke tests.

## Rejected Alternatives

- Render: rejected for the first pilot because the operator prefers direct VPS control over managed platform conventions.
- Railway: rejected because it optimizes for fast app hosting but gives less direct control over host-level backup and recovery procedures.
- AWS ECS: rejected because it adds IAM, networking, registry, and service orchestration overhead before the pilot has production traffic that justifies it.

## Required Resources

| Environment | Resource | Owner | Backup | Retention | Cost Expectation |
|-------------|----------|-------|--------|-----------|------------------|
| staging | 1 VPS running Docker Compose API, worker, PostgreSQL, Redis | founder/operator | nightly PostgreSQL custom-format dump before migration tests | 7 days | low fixed monthly VPS cost |
| production | 1 VPS running Docker Compose API, worker, PostgreSQL, Redis | founder/operator | daily PostgreSQL custom-format dump and pre-migration dump | 30 days minimum during pilot | low fixed monthly VPS cost plus backup storage |
| staging | environment secret file on host | founder/operator | not backed up as plaintext; recreate from secret store | rotate on exposure or staff change | included in VPS ops |
| production | environment secret file on host | founder/operator | not backed up as plaintext; recreate from secret store | rotate on exposure or staff change | included in VPS ops |
| both | logs from Docker containers | founder/operator | exported only when needed for incidents with PII review | 14 days local retention | included in VPS disk budget |

## Deployment Commands

Staging deploy command shape:

```bash
ssh "$STAGING_VPS_USER@$STAGING_VPS_HOST" \
  "cd /srv/lead-sla-agent && git fetch --prune && git checkout $GITHUB_SHA && docker compose config && docker compose up -d postgres redis && docker compose run --rm api alembic upgrade head && docker compose up -d --build api worker && docker compose ps"
```

Production deploy command shape:

```bash
ssh "$PRODUCTION_VPS_USER@$PRODUCTION_VPS_HOST" \
  "cd /srv/lead-sla-agent && BACKUP_PATH=backups/pre-migration-$GITHUB_SHA.dump ./scripts/backup_postgres.sh && git fetch --prune && git checkout $GITHUB_SHA && docker compose config && docker compose up -d postgres redis && docker compose run --rm api alembic upgrade head && docker compose up -d --build api worker && docker compose ps"
```

Rollback command shape:

```bash
ssh "$PRODUCTION_VPS_USER@$PRODUCTION_VPS_HOST" \
  "cd /srv/lead-sla-agent && git checkout $ROLLBACK_GIT_SHA && docker compose up -d --build api worker && docker compose ps"
```

Database restore remains a separate explicit decision and uses `scripts/restore_postgres.sh` against a selected backup.

## Consequences

- The first pilot can run without adopting a larger cloud orchestration layer.
- The operator owns OS updates, firewall rules, Docker installation, disk capacity, backups, and restore drills.
- Staging and production separation depends on disciplined host and secret separation.
- A future move to Render, Fly.io, Railway, ECS, or Kubernetes requires a new ADR and migration plan.
