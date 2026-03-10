#!/usr/bin/env bash
# =============================================================================
# scripts/superset/setup_odoo_superset.sh
# =============================================================================
# Wire Odoo PostgreSQL to Apache Superset (read-only connection).
#
# Steps performed:
#   1. Create `superset_ro` read-only role in Odoo PostgreSQL
#   2. Grant SELECT on all Odoo finance views to superset_ro
#   3. Deploy SQL views from infra/superset/virtual_datasets.sql into Odoo DB
#   4. Register the Odoo database connection in Superset via API
#   5. Register each dataset (view) in Superset via API
#
# Required env vars (set in .env or export before running):
#   ODOO_PG_HOST        — host of Odoo PostgreSQL (e.g. 178.128.112.214)
#   ODOO_PG_PORT        — port (default: 5432)
#   ODOO_PG_USER        — admin user (e.g. odoo)
#   ODOO_PG_PASSWORD    — admin password
#   ODOO_PG_DB          — database name (e.g. odoo)
#   ODOO_SUPERSET_RO_PASS — password for new superset_ro role
#   SUPERSET_URL        — Superset base URL (e.g. https://superset.insightpulseai.com)
#   SUPERSET_USERNAME   — Superset admin username
#   SUPERSET_PASSWORD   — Superset admin password
#
# Usage:
#   export $(cat .env.local | xargs)
#   ./scripts/superset/setup_odoo_superset.sh
#
#   # Dry run (only shows what would be done):
#   DRY_RUN=1 ./scripts/superset/setup_odoo_superset.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VIEWS_SQL="${REPO_ROOT}/infra/superset/virtual_datasets.sql"

# ── env validation ────────────────────────────────────────────────────────────
: "${ODOO_PG_HOST:?ODOO_PG_HOST is required}"
: "${ODOO_PG_USER:?ODOO_PG_USER is required}"
: "${ODOO_PG_PASSWORD:?ODOO_PG_PASSWORD is required}"
: "${ODOO_PG_DB:=odoo}"
: "${ODOO_PG_PORT:=5432}"
: "${ODOO_SUPERSET_RO_PASS:?ODOO_SUPERSET_RO_PASS is required}"
: "${SUPERSET_URL:?SUPERSET_URL is required}"
: "${SUPERSET_USERNAME:?SUPERSET_USERNAME is required}"
: "${SUPERSET_PASSWORD:?SUPERSET_PASSWORD is required}"

DRY_RUN="${DRY_RUN:-0}"
DB_UUID="7c8d9e01-0f11-4a12-b134-0000000001db"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
log_dry() { echo "[DRY-RUN] $*"; }

run_psql() {
    PGPASSWORD="${ODOO_PG_PASSWORD}" psql \
        -h "${ODOO_PG_HOST}" \
        -p "${ODOO_PG_PORT}" \
        -U "${ODOO_PG_USER}" \
        -d "${ODOO_PG_DB}" \
        "$@"
}

# ── step 1: create superset_ro role ──────────────────────────────────────────
log "Step 1: Creating superset_ro read-only role in ${ODOO_PG_DB}..."

CREATE_ROLE_SQL=$(cat <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'superset_ro') THEN
        CREATE ROLE superset_ro WITH LOGIN PASSWORD '${ODOO_SUPERSET_RO_PASS}';
        RAISE NOTICE 'Created role superset_ro';
    ELSE
        ALTER ROLE superset_ro WITH PASSWORD '${ODOO_SUPERSET_RO_PASS}';
        RAISE NOTICE 'Updated password for existing role superset_ro';
    END IF;
END
\$\$;

-- Grant connect on database
GRANT CONNECT ON DATABASE ${ODOO_PG_DB} TO superset_ro;

-- Grant usage on public schema
GRANT USAGE ON SCHEMA public TO superset_ro;

-- Grant SELECT on all existing tables/views
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_ro;

-- Grant SELECT on future tables/views (for newly installed Odoo modules)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO superset_ro;
SQL
)

if [[ "${DRY_RUN}" == "1" ]]; then
    log_dry "Would execute SQL: CREATE ROLE superset_ro + GRANT SELECT ON ALL TABLES"
else
    echo "${CREATE_ROLE_SQL}" | run_psql
    log "✅ superset_ro role configured"
fi

# ── step 2: deploy views into Odoo PostgreSQL ─────────────────────────────────
log "Step 2: Deploying finance views from virtual_datasets.sql..."

if [[ ! -f "${VIEWS_SQL}" ]]; then
    log "WARNING: ${VIEWS_SQL} not found — skipping view deployment"
else
    if [[ "${DRY_RUN}" == "1" ]]; then
        log_dry "Would deploy ${VIEWS_SQL} to ${ODOO_PG_DB}"
    else
        run_psql -f "${VIEWS_SQL}"
        log "✅ Finance views deployed"
    fi
fi

# ── step 3: get Superset access token ────────────────────────────────────────
log "Step 3: Authenticating with Superset at ${SUPERSET_URL}..."

if [[ "${DRY_RUN}" == "1" ]]; then
    log_dry "Would POST /api/v1/security/login to get access token"
    ACCESS_TOKEN="dry-run-token"
else
    AUTH_RESPONSE=$(curl -sf -X POST "${SUPERSET_URL}/api/v1/security/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"${SUPERSET_USERNAME}\",\"password\":\"${SUPERSET_PASSWORD}\",\"provider\":\"db\",\"refresh\":false}")
    ACCESS_TOKEN=$(echo "${AUTH_RESPONSE}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
    log "✅ Authenticated (token: ${ACCESS_TOKEN:0:15}...)"
fi

superset_api() {
    local method="$1"
    local path="$2"
    local body="${3:-}"
    if [[ "${DRY_RUN}" == "1" ]]; then
        log_dry "${method} ${SUPERSET_URL}${path}"
        return 0
    fi
    if [[ -n "${body}" ]]; then
        curl -sf -X "${method}" "${SUPERSET_URL}${path}" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "${body}"
    else
        curl -sf -X "${method}" "${SUPERSET_URL}${path}" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}"
    fi
}

# ── step 4: register database connection in Superset ─────────────────────────
log "Step 4: Registering Odoo database connection in Superset..."

DB_PAYLOAD=$(python3 -c "
import json
payload = {
    'database_name': 'Odoo Direct (Read-Only)',
    'sqlalchemy_uri': 'postgresql+psycopg2://superset_ro:${ODOO_SUPERSET_RO_PASS}@${ODOO_PG_HOST}:${ODOO_PG_PORT}/${ODOO_PG_DB}',
    'expose_in_sqllab': True,
    'allow_ctas': False,
    'allow_cvas': False,
    'allow_dml': False,
    'allow_run_async': True,
    'cache_timeout': 300,
    'extra': json.dumps({
        'engine_params': {'connect_args': {'sslmode': 'prefer'}},
        'schema_cache_timeout': 600
    })
}
print(json.dumps(payload))
")

# Check if database already exists
EXISTING_DBS=$(superset_api GET "/api/v1/database/?q=(filters:!((col:database_name,opr:DatabaseStartsWith,val:'Odoo')))" 2>/dev/null || echo '{}')
if echo "${EXISTING_DBS}" | python3 -c "import json,sys; r=json.load(sys.stdin); exit(0 if r.get('count',0)>0 else 1)" 2>/dev/null; then
    log "⚠️  Database 'Odoo Direct (Read-Only)' already exists in Superset — skipping creation"
    DB_ID=$(echo "${EXISTING_DBS}" | python3 -c "import json,sys; r=json.load(sys.stdin); print(r['result'][0]['id'])" 2>/dev/null || echo "unknown")
    log "   Existing DB id: ${DB_ID}"
else
    if [[ "${DRY_RUN}" == "1" ]]; then
        log_dry "Would POST /api/v1/database/ with Odoo connection config"
        DB_ID="dry-run-db-id"
    else
        DB_RESPONSE=$(superset_api POST "/api/v1/database/" "${DB_PAYLOAD}")
        DB_ID=$(echo "${DB_RESPONSE}" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
        log "✅ Database registered (id: ${DB_ID})"
    fi
fi

# ── step 5: register datasets (views) ────────────────────────────────────────
log "Step 5: Registering Odoo finance view datasets in Superset..."

VIEWS=(
    "vw_bir_withholding_summary:invoice_date:BIR Withholding Tax Summary"
    "vw_consolidated_trial_balance:period:Consolidated Trial Balance"
    "vw_ap_aging:invoice_date:AP Aging Report"
    "vw_ar_aging:invoice_date:AR Aging Report"
    "vw_expense_analytics:expense_date:Expense Analytics"
    "vw_cash_position:last_transaction_date:Cash Position Summary"
)

for VIEW_DEF in "${VIEWS[@]}"; do
    IFS=: read -r VIEW_NAME DTTM_COL VIEW_DESC <<< "${VIEW_DEF}"

    if [[ "${DRY_RUN}" == "1" ]]; then
        log_dry "Would register dataset: ${VIEW_NAME}"
        continue
    fi

    DATASET_PAYLOAD=$(python3 -c "
import json
print(json.dumps({
    'database': int('${DB_ID}'),
    'schema': 'public',
    'table_name': '${VIEW_NAME}',
    'description': '${VIEW_DESC}',
    'main_dttm_col': '${DTTM_COL}',
    'filter_select_enabled': True,
    'cache_timeout': 300
}))
")

    # Check if dataset already exists
    EXISTING_DS=$(superset_api GET "/api/v1/dataset/?q=(filters:!((col:table_name,opr:DatasetIsNullOrEmpty,val:'${VIEW_NAME}')))" 2>/dev/null || echo '{}')
    if echo "${EXISTING_DS}" | python3 -c "import json,sys; r=json.load(sys.stdin); exit(0 if r.get('count',0)>0 else 1)" 2>/dev/null; then
        log "  ⚠️  Dataset '${VIEW_NAME}' already exists — skipping"
    else
        DS_RESPONSE=$(superset_api POST "/api/v1/dataset/" "${DATASET_PAYLOAD}" || true)
        DS_ID=$(echo "${DS_RESPONSE}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id','error'))" 2>/dev/null || echo "error")
        if [[ "${DS_ID}" == "error" ]]; then
            log "  ⚠️  Failed to create dataset '${VIEW_NAME}' (view may not exist yet)"
        else
            log "  ✅ Dataset '${VIEW_NAME}' registered (id: ${DS_ID})"
        fi
    fi
done

# ── summary ──────────────────────────────────────────────────────────────────
echo ""
log "============================================================"
log "Superset Connector Setup Complete"
log "============================================================"
log "Database:  Odoo Direct (Read-Only)"
log "Datasets:  ${#VIEWS[@]} views registered"
log "Superset:  ${SUPERSET_URL}/tablemodelview/list/"
log ""
log "Next steps:"
log "  1. Open Superset → SQL Lab → select 'Odoo Direct (Read-Only)'"
log "  2. Run: SELECT * FROM vw_ar_aging LIMIT 10;"
log "  3. Create charts from the registered datasets"
log "  4. For embedded dashboards, set SUPERSET_GUEST_TOKEN_SECRET in .env"
log "============================================================"

if [[ "${DRY_RUN}" == "1" ]]; then
    echo ""
    log "DRY RUN completed — no changes were made"
fi
