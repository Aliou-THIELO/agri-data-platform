#!/usr/bin/env bash
set -euo pipefail
for f in sql/migrations/*.sql; do
  echo "== $f"
  docker compose exec -T postgres psql -U "${POSTGRES_USER:-agri_user}" -d "${POSTGRES_DB:-agri_db}" -v ON_ERROR_STOP=1 < "$f"
done
