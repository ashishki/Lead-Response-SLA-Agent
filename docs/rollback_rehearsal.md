# Rollback Rehearsal Record

Use this artifact for each staging release rehearsal before production promotion.

environment: staging
release_candidate_sha: TBD
rollback_git_sha: TBD
migration_version_before: TBD
migration_version_after: TBD
rollback_decision: app-only | migration-downgrade | restore-backup
backup_path: TBD
smoke_result: TBD
rehearsed_at_utc: TBD
operator: TBD

Required command shape:

```bash
python scripts/rollback_check.py --rehearsal-artifact docs/rollback_rehearsal.md
alembic current
alembic downgrade -1
alembic current
alembic upgrade head
python scripts/smoke_test.py --environment staging --base-url https://staging.example.test --tenant-id smoke-staging --sandbox-mode
```

Decision notes:

- Use `app-only` when the release failed after deployment but the database migration completed and the schema remains compatible with the previous image.
- Use `migration-downgrade` only when the migration has downgrade coverage and the release notes confirm no irreversible data transformation.
- Use `restore-backup` when data was corrupted, a migration is irreversible, or downgrade validation fails.
