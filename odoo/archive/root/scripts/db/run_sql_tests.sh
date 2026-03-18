#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_DB_URL:?Missing SUPABASE_DB_URL}"

EXPOSED_JSON="$(python3 scripts/supabase/exposed_schemas.py)"
EXPOSED="$(echo "$EXPOSED_JSON" | python3 -c 'import sys,json; print(",".join(json.load(sys.stdin)["schemas_exposed_by_api"]))')"

echo "[sql-tests] exposed schemas: $EXPOSED"

# We set a session setting used by the DO blocks.
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<SQL
set app.exposed_schemas = '$EXPOSED';
SQL

for f in tests/sql/*.sql; do
  echo "[sql-tests] running $f"
  psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$f"
done

echo "[sql-tests] OK"
