#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"

req_files=(
  "docs/operations/MULTI_COMPANY_SEEDING.md"
  "docs/operations/MONTH_END_CLOSE_MAPPING.md"
  "docs/operations/MONTH_END_CLOSE_IMPLEMENTATION.md"
  "scripts/seed_companies_users.py"
  "scripts/odoo/seed_org_companies_users_integrations.py"
  "scripts/rollback_seed_org.sql"
)

missing=0
for f in "${req_files[@]}"; do
  if [[ ! -f "$ROOT/$f" ]]; then
    echo "MISSING: $f"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "❌ Required SSOT artifacts are missing."
  exit 1
fi

echo "✅ Required SSOT artifacts present."
