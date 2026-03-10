#!/usr/bin/env bash
# Generates a deterministic "Supabase Project Context Pack"
# Extracts schemas, tables, policies, functions, triggers, and extensions into docs/supabase/context/
#
# Prerequisites:
# - Supabase CLI installed
# - Valid SUPABASE_DB_PASSWORD exposed in environment (if querying remote)
# - Run from project root

set -euo pipefail

OUT_DIR="/tmp/supabase-context"
mkdir -p "$OUT_DIR"

echo "==== Generating Supabase Project Context Pack ===="
echo "Target: $OUT_DIR"
echo ""

# Fallback PG connection string if CLI is not configured
DB_URL="${SUPABASE_DB_URL:-""}"

# Helper to run SQL deterministically (sorted)
run_sql() {
  local query="$1"
  local out_file="$2"

  echo "Extracting: $(basename "$out_file")"

  if [ -n "$DB_URL" ]; then
    psql "$DB_URL" -qAt -c "$query" > "$out_file"
  else
    # Assume local supabase db is running
    supabase db psql -qAt -c "$query" > "$out_file" 2>/dev/null || {
      echo "[ERROR] Could not connect via supabase db psql. Is the db running or SUPABASE_DB_URL set?"
      exit 1
    }
  fi
}

# 1) Full logical schema (Tables, Columns, PK/FK)
run_sql "
SELECT
  table_schema, table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name, ordinal_position;
" "$OUT_DIR/schema.sql"

# 2) RLS Policies
run_sql "
SELECT
  schemaname, tablename, policyname, roles, cmd, qual, with_check
FROM pg_policies
ORDER BY schemaname, tablename, policyname;
" "$OUT_DIR/rls_policies.sql"

# 3) Extensions
run_sql "
SELECT extname, extversion
FROM pg_extension
ORDER BY extname;
" "$OUT_DIR/extensions.sql"

# 4) Functions
run_sql "
SELECT
  n.nspname as schema,
  p.proname as name,
  pg_get_function_arguments(p.oid) as args,
  pg_get_function_result(p.oid) as return_type
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'graphql', 'graphql_public')
ORDER BY n.nspname, p.proname;
" "$OUT_DIR/functions.sql"

# 5) Triggers
run_sql "
SELECT
  event_object_schema as schema,
  event_object_table as table,
  trigger_name,
  action_timing,
  event_manipulation as event,
  action_statement as definition
FROM information_schema.triggers
WHERE event_object_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY event_object_schema, event_object_table, trigger_name;
" "$OUT_DIR/triggers.sql"

# 6) Indexes (and Constraints constraints roughly mapped to indexes)
run_sql "
SELECT
  schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename, indexname;
" "$OUT_DIR/indexes.sql"

# 7) Grants
run_sql "
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name, grantee, privilege_type;
" "$OUT_DIR/grants.sql"

# Write README
cat << 'EOF' > "$OUT_DIR/README.md"
# Supabase Project Context Pack

This directory contains a deterministic, machine-readable + human-readable dump of the Supabase project configuration (schemas, functions, RLS, triggers, etc).

**Purpose**: Provide an LLM-friendly, complete context of the database layer without dumping raw rows.

**Generated via**: `scripts/db/generate_supabase_context_pack.sh`

## Artifacts
- `schema.sql`: Table/column inventory.
- `rls_policies.sql`: RLS definitions.
- `functions.sql`: Signatures of custom database functions.
- `triggers.sql`: Table triggers.
- `indexes.sql`: Database index architecture.
- `extensions.sql`: Enabled pg extensions.
- `grants.sql`: Role table grants.
EOF

echo "==== Done ===="
echo "Context pack written to $OUT_DIR/"
