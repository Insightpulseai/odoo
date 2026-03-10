#!/usr/bin/env bash
# check_supabase_contract.sh — Enforce Supabase directory contract
#
# Rules enforced:
#   1. supabase/migrations/ directory must exist
#   2. supabase/functions/  directory must exist
#   3. No .sql files outside supabase/migrations/ or supabase/seed/
#      (with documented EXCEPTIONS for pre-existing non-Supabase SQL paths)
#
# CI: supabase-contract-guard.yml
# Docs: docs/architecture/CANONICAL_MONOREPO_LAYOUT.md
#
# Usage:
#   bash scripts/ci/check_supabase_contract.sh
#   ROOT=/path/to/repo bash scripts/ci/check_supabase_contract.sh

set -euo pipefail

ROOT="${ROOT:-.}"
FAIL=0

# ---------------------------------------------------------------------------
# EXCEPTIONS — pre-existing SQL paths that are NOT Supabase migrations
# Each entry is a path prefix or exact path (relative to repo root).
# EXCEPTION: db/ — Postgres schema/migration scripts for DO-managed Postgres
#            (not Supabase). Used by Odoo database layer.
# EXCEPTION: dev/postgres-init/ — Docker Compose local dev init scripts.
# EXCEPTION: docs/ — Schema documentation SQL (read-only reference files).
# EXCEPTION: infra/databricks/ — Databricks lake SQL (non-Supabase).
# ---------------------------------------------------------------------------
EXCEPTION_PREFIXES=(
  "db/"
  "dev/postgres-init/"
  "docs/"
  "infra/databricks/"
)

# ---------------------------------------------------------------------------
# Helper: is path in exceptions?
# ---------------------------------------------------------------------------
is_exception() {
  local filepath="$1"
  for prefix in "${EXCEPTION_PREFIXES[@]}"; do
    if [[ "${filepath}" == "${prefix}"* ]]; then
      return 0
    fi
  done
  return 1
}

# ---------------------------------------------------------------------------
# Rule 1: supabase/ directory must exist
# ---------------------------------------------------------------------------
if [[ ! -d "${ROOT}/supabase" ]]; then
  echo "::error file=supabase::supabase/ directory is missing — Supabase contract violated"
  FAIL=1
else
  echo "[OK] supabase/ directory exists"
fi

# ---------------------------------------------------------------------------
# Rule 2: supabase/migrations/ must exist
# ---------------------------------------------------------------------------
if [[ ! -d "${ROOT}/supabase/migrations" ]]; then
  echo "::error file=supabase/migrations::supabase/migrations/ directory is missing"
  FAIL=1
else
  echo "[OK] supabase/migrations/ directory exists"
  # Soft warning if empty
  SQL_COUNT=$(git -C "${ROOT}" ls-files 'supabase/migrations/*.sql' 2>/dev/null | wc -l | tr -d ' ')
  if [[ "${SQL_COUNT}" -eq 0 ]]; then
    echo "::warning::supabase/migrations/ contains no .sql files — is this intentional?"
  else
    echo "[OK] supabase/migrations/ contains ${SQL_COUNT} migration file(s)"
  fi
fi

# ---------------------------------------------------------------------------
# Rule 3: supabase/functions/ must exist
# ---------------------------------------------------------------------------
if [[ ! -d "${ROOT}/supabase/functions" ]]; then
  echo "::error file=supabase/functions::supabase/functions/ directory is missing"
  FAIL=1
else
  echo "[OK] supabase/functions/ directory exists"
fi

# ---------------------------------------------------------------------------
# Rule 4: No stray .sql files outside supabase/migrations/ or supabase/seed/
# ---------------------------------------------------------------------------
echo ""
echo "Checking for stray .sql files outside supabase/migrations/ and supabase/seed/ ..."

STRAY_FOUND=0
while IFS= read -r filepath; do
  # Skip allowed supabase paths
  if [[ "${filepath}" == supabase/migrations/* ]] \
    || [[ "${filepath}" == supabase/seed/* ]] \
    || [[ "${filepath}" == supabase/seeds/* ]]; then
    continue
  fi

  # Skip documented exceptions
  if is_exception "${filepath}"; then
    echo "  [EXCEPTION] ${filepath}"
    continue
  fi

  # Fail on any other .sql file
  echo "::error file=${filepath}::Stray SQL file detected outside supabase/migrations/ or supabase/seed/. Move to supabase/migrations/ or add to EXCEPTION_PREFIXES in check_supabase_contract.sh."
  STRAY_FOUND=1
  FAIL=1
done < <(git -C "${ROOT}" ls-files '*.sql' 2>/dev/null)

if [[ "${STRAY_FOUND}" -eq 0 ]]; then
  echo "[OK] No stray SQL files found outside permitted paths"
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
echo ""
if [[ "${FAIL}" -ne 0 ]]; then
  echo "FAIL: Supabase contract violations found. See annotations above."
  exit 1
fi

echo "PASS: Supabase directory contract satisfied."
exit 0
