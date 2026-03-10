#!/usr/bin/env bash
set -euo pipefail
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="backups/pg_${TS}.sql.gz"

mkdir -p backups
docker compose exec -T db bash -lc 'pg_dump -U odoo -d odoo' | gzip -9 > "${OUT}"
echo "Wrote ${OUT}"
