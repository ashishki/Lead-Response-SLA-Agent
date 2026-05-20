#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 2
fi

backup_path="${BACKUP_PATH:-backups/lead_sla_$(date -u +%Y%m%dT%H%M%SZ).dump}"
mkdir -p "$(dirname "$backup_path")"

pg_dump \
  --format=custom \
  --no-owner \
  --no-acl \
  --file "$backup_path" \
  "$DATABASE_URL"

echo "backup_path=$backup_path"
