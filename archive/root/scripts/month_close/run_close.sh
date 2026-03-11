#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_URL:?}"
: "${SUPABASE_SERVICE_ROLE_KEY:?}"
: "${ODOO_URL:?}"
: "${ODOO_DB:?}"
: "${ODOO_API_KEY:?}"
: "${ORG_ID:?}"  # registry.orgs.id

PERIOD="${1:-$(date -u -d "$(date +%Y-%m-01) -1 day" +%Y-%m)}"
SCOPE="${2:-local}"

echo "▶ Month close run: period=$PERIOD scope=$SCOPE org=$ORG_ID"

node scripts/month_close/run_close.mjs "$PERIOD" "$SCOPE"
