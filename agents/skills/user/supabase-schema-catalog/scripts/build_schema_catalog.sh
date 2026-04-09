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
echo "  SQL: $SQL_FILE"
echo "  OUT: $OUT_FILE"

# Optional: comma-separated schema list, e.g. 'public,realm,scout'
SCHEMA_FILTER="${SCHEMA_FILTER:-}"

mkdir -p "$SKILL_DIR/catalog"

if [[ -n "$SCHEMA_FILTER" ]]; then
  echo "  SCHEMA_FILTER: $SCHEMA_FILTER"
  # Pass SCHEMA_FILTER as a custom GUC to Postgres via PSQLRC
  PSQLRC_TMP="$(mktemp)"
  echo "\\set SCHEMA_FILTER '$SCHEMA_FILTER'" > "$PSQLRC_TMP"
  PSQLRC_OLD="${PSQLRC:-}"
  export PSQLRC="$PSQLRC_TMP"

  psql "$SUPABASE_DB_URL" \
    -v ON_ERROR_STOP=1 \
    -f "$SQL_FILE" \
    -t -A > "$OUT_FILE"

  # Cleanup
  rm -f "$PSQLRC_TMP"
  export PSQLRC="$PSQLRC_OLD"
else
  psql "$SUPABASE_DB_URL" \
    -v ON_ERROR_STOP=1 \
    -f "$SQL_FILE" \
    -t -A > "$OUT_FILE"
fi

echo "Schema catalog written to: $OUT_FILE"
