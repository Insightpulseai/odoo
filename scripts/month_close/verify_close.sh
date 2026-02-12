#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_DATABASE_URL:?}"
: "${ORG_ID:?}"

echo "🔎 Checking Supabase schemas..."
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\dn+" | sed -n '1,120p'
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\dt tax.*"
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\dt analytics.kpi_points"
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\dt audit.events"

echo "🔎 Checking required RPCs..."
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\df ops.month_close_%"
psql "$SUPABASE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "\df analytics.month_close_%"

echo "✅ Verification passed."
