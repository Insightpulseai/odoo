#!/usr/bin/env bash
set -euo pipefail

# Repo-owned Supabase "preview" gate:
# - starts ephemeral db (via Supabase CLI local stack)
# - applies migrations
# - runs lightweight validation queries
# - exports logs as artifact-friendly files

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [ ! -d supabase ]; then
  echo "[supabase-preview] missing ./supabase directory" >&2
  exit 2
fi

# Ensure Supabase CLI exists
if ! command -v supabase >/dev/null 2>&1; then
  echo "[supabase-preview] supabase CLI not found. Install in CI via setup step." >&2
  exit 2
fi

# Keep logs in repo workspace for upload as artifacts
mkdir -p .ci_artifacts/supabase
LOGDIR=".ci_artifacts/supabase"

echo "[supabase-preview] supabase version: $(supabase --version)"
echo "[supabase-preview] starting local services..."
supabase start 2>&1 | tee "$LOGDIR/supabase_start.log"

echo "[supabase-preview] applying migrations (db reset)..."
# db reset is deterministic for CI previews; it rebuilds from migrations + seeds
supabase db reset 2>&1 | tee "$LOGDIR/supabase_db_reset.log"

echo "[supabase-preview] smoke query..."
# Requires psql; Supabase CLI outputs connection info via status.
STATUS_JSON="$(supabase status -o json)"
echo "$STATUS_JSON" > "$LOGDIR/supabase_status.json"

DB_URL="$(python3 - <<'PY'
import json,sys
j=json.load(sys.stdin)
print(j["DB_URL"])
PY
<<<"$STATUS_JSON")"

# Basic sanity checks (customize as needed)
psql "$DB_URL" -v ON_ERROR_STOP=1 -c "select 1 as ok;" 2>&1 | tee "$LOGDIR/psql_smoke.log"

echo "[supabase-preview] done"
echo "[supabase-preview] artifacts at $LOGDIR"
