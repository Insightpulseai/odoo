#!/usr/bin/env bash
# =============================================================================
# Supabase SQL + RLS Checks
# =============================================================================
# Validates:
#   1. Exposed schemas exist in database
#   2. RLS is enabled on protected tables
#   3. RLS policies exist for protected tables
#
# Usage:
#   DATABASE_URL="postgresql://..." ./scripts/supabase/checks.sh
#
# Required environment:
#   DATABASE_URL - PostgreSQL connection string (admin/service role)
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CFG="$ROOT/supabase/config.toml"

: "${DATABASE_URL:?DATABASE_URL is required (service role / admin connection string)}"

if [[ ! -f "$CFG" ]]; then
  echo "[supabase-checks] missing $CFG" >&2
  exit 1
fi

# =============================================================================
# Extract exposed schemas from supabase/config.toml
# =============================================================================
# Supports:
#   schemas = ["public","graphql_public"]
# or:
#   [api]
#   schemas = ["public","graphql_public"]

schemas_csv="$(
  awk '
    $0 ~ /^[[:space:]]*schemas[[:space:]]*=/ {
      gsub(/.*=\s*\[/, "", $0);
      gsub(/\].*/, "", $0);
      gsub(/"/, "", $0);
      gsub(/[[:space:]]*/, "", $0);
      print $0;
      exit
    }
  ' "$CFG"
)"

if [[ -z "${schemas_csv:-}" ]]; then
  echo "[supabase-checks] could not parse exposed schemas from supabase/config.toml" >&2
  exit 1
fi

# Convert "public,graphql_public" -> "('public','graphql_public')"
schema_list="('$(echo "$schemas_csv" | sed "s/,/','/g")')"

# =============================================================================
# Define RLS-protected tables
# =============================================================================
# Critical tables that MUST have RLS enabled and policies defined.
# Organized by domain for clarity.

table_list="(
  'ops.jobs',
  'ops.job_runs',
  'ops.job_events',
  'afc.close_calendar',
  'afc.closing_task',
  'afc.gl_posting',
  'afc.sod_audit_log',
  'qms.controlled_docs',
  'qms.doc_versions',
  'qms.approvals',
  'qms.audit_events',
  'kb.glossary_terms',
  'kb.journeys',
  'kb.journey_steps'
)"

# Remove newlines and extra spaces for SQL injection safety
table_list="$(echo "$table_list" | tr -d '\n' | sed 's/  */ /g')"

echo "[supabase-checks] exposed schemas: $schema_list"
echo "[supabase-checks] rls tables: $table_list"

# =============================================================================
# Verify database connectivity
# =============================================================================
if ! psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "select 1" >/dev/null 2>&1; then
  echo "[supabase-checks] cannot connect to database" >&2
  echo "[supabase-checks] ensure DATABASE_URL is valid and accessible" >&2
  exit 1
fi

echo "[supabase-checks] database connection verified"

# =============================================================================
# Prepare temporary directory for SQL files
# =============================================================================
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

# =============================================================================
# Inject schema/table lists into SQL templates
# =============================================================================
sed "s/__SCHEMA_LIST__/$schema_list/g" \
  "$ROOT/scripts/supabase/sql/assert_exposed_schemas.sql" > "$tmpdir/assert_exposed_schemas.sql"

sed "s/__TABLE_LIST__/$table_list/g" \
  "$ROOT/scripts/supabase/sql/assert_rls_enabled.sql" > "$tmpdir/assert_rls_enabled.sql"

sed "s/__TABLE_LIST__/$table_list/g" \
  "$ROOT/scripts/supabase/sql/assert_policies_exist.sql" > "$tmpdir/assert_policies_exist.sql"

# =============================================================================
# Run checks
# =============================================================================
echo "[supabase-checks] running schema checks..."
if ! psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_exposed_schemas.sql" 2>&1; then
  echo "[supabase-checks] FAILED: schema checks" >&2
  exit 1
fi
echo "[supabase-checks] schema checks passed"

echo "[supabase-checks] running RLS checks..."
if ! psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_rls_enabled.sql" 2>&1; then
  echo "[supabase-checks] FAILED: RLS checks" >&2
  exit 1
fi
echo "[supabase-checks] RLS checks passed"

echo "[supabase-checks] running policy checks..."
if ! psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_policies_exist.sql" 2>&1; then
  echo "[supabase-checks] FAILED: policy checks" >&2
  exit 1
fi
echo "[supabase-checks] policy checks passed"

echo "[supabase-checks] OK - all checks passed"
