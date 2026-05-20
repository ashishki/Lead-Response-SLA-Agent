#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 2
fi

if [[ -z "${BACKUP_PATH:-}" ]]; then
  echo "BACKUP_PATH is required" >&2
  exit 2
fi

if [[ ! -f "$BACKUP_PATH" ]]; then
  echo "backup file does not exist" >&2
  exit 2
fi

pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  --dbname "$DATABASE_URL" \
  "$BACKUP_PATH"

if [[ -n "${VERIFY_COMMAND:-}" ]]; then
  bash -lc "$VERIFY_COMMAND"
fi
