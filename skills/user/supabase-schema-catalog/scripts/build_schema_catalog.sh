#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQL_FILE="$SKILL_DIR/scripts/build_schema_catalog.sql"
OUT_FILE="$SKILL_DIR/catalog/schema_catalog.json"

if [[ -z "${SUPABASE_DB_URL:-}" ]]; then
  echo "ERROR: SUPABASE_DB_URL is not set."
  echo "Set it to your Supabase Postgres connection string and retry."
  exit 1
fi

echo "Building Supabase schema catalog..."
echo "  DB: (hidden)"
echo "  SQL: $SQL_FILE"
echo "  OUT: $OUT_FILE"

# Optional comma-separated schema list: e.g. 'public,realm,scout'
SCHEMA_FILTER="${SCHEMA_FILTER:-}"

# Create catalog directory if missing
mkdir -p "$SKILL_DIR/catalog"

# Run query and write JSON
if [[ -n "$SCHEMA_FILTER" ]]; then
  echo "  SCHEMA_FILTER: $SCHEMA_FILTER"
  psql "$SUPABASE_DB_URL" \
    -v ON_ERROR_STOP=1 \
    -v SCHEMA_FILTER="$SCHEMA_FILTER" \
    -f "$SQL_FILE" \
    -t -A > "$OUT_FILE"
else
  psql "$SUPABASE_DB_URL" \
    -v ON_ERROR_STOP=1 \
    -f "$SQL_FILE" \
    -t -A > "$OUT_FILE"
fi

echo "Schema catalog written to: $OUT_FILE"
