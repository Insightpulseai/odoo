#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CFG="$ROOT/supabase/config.toml"

: "${DATABASE_URL:?DATABASE_URL is required (service role / admin connection string)}"

if [[ ! -f "$CFG" ]]; then
  echo "[supabase-checks] missing $CFG" >&2
  exit 1
fi

# Extract exposed schemas from supabase/config.toml
# Supports either:
#   schemas = ["public","ops"]
# or:
#   [api]
#   schemas = ["public","ops"]
#
# If your config differs, adjust the parser (keep deterministic).
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

# Convert "public,ops" -> "('public','ops')"
schema_list="('$(echo "$schemas_csv" | sed "s/,/','/g")')"

# Define RLS-critical tables list.
# TODO: Replace with your canonical protected tables.
# Keep it minimal at first; expand as you formalize.
table_list="('ops.secrets','ops.secret_access_log','ops.audit_logs')"

echo "[supabase-checks] exposed schemas: $schema_list"
echo "[supabase-checks] rls tables: $table_list"

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -c "select 1" >/dev/null

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

# Inject lists into SQL templates
sed "s/__SCHEMA_LIST__/$schema_list/g" \
  "$ROOT/scripts/supabase/sql/assert_exposed_schemas.sql" > "$tmpdir/assert_exposed_schemas.sql"

sed "s/__TABLE_LIST__/$table_list/g" \
  "$ROOT/scripts/supabase/sql/assert_rls_enabled.sql" > "$tmpdir/assert_rls_enabled.sql"

sed "s/__TABLE_LIST__/$table_list/g" \
  "$ROOT/scripts/supabase/sql/assert_policies_exist.sql" > "$tmpdir/assert_policies_exist.sql"

echo "[supabase-checks] running schema checks..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_exposed_schemas.sql"

echo "[supabase-checks] running RLS checks..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_rls_enabled.sql"

echo "[supabase-checks] running policy checks..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmpdir/assert_policies_exist.sql"

echo "[supabase-checks] OK"
