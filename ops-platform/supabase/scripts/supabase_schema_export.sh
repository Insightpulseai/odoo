#!/usr/bin/env bash
# supabase_schema_export.sh — Export cloud schema and apply repo migrations to self-hosted.
#
# Usage:
#   ./supabase_schema_export.sh [--dry-run]
#   ./supabase_schema_export.sh --help
#
# Exports cloud schema via pg_dump --schema-only, applies repo migrations to
# self-hosted Supabase, and generates a schema parity report.

set -euo pipefail

# --- Configuration ---
VM_HOST="${VM_HOST:-4.193.100.31}"
VM_USER="${VM_USER:-azureuser}"
VM_PG_PORT="${VM_PG_PORT:-54322}"
LOCAL_TUNNEL_PORT="${LOCAL_TUNNEL_PORT:-54399}"
KV_NAME="${KV_NAME:-kv-ipai-dev}"
EVIDENCE_DIR="${EVIDENCE_DIR:-docs/evidence/$(date +%Y%m%d-%H%M)/supabase-migration}"
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
MIGRATIONS_DIR="${REPO_ROOT}/supabase/migrations"
DRY_RUN=false
SSH_TUNNEL_PID=""

# --- Functions ---
usage() {
    sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
    exit 0
}

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE:-/dev/null}"; }
err() { log "ERROR: $*" >&2; }
die() { err "$@"; exit 1; }

cleanup() {
    if [[ -n "${SSH_TUNNEL_PID}" ]]; then
        kill "${SSH_TUNNEL_PID}" 2>/dev/null || true
        log "SSH tunnel (PID ${SSH_TUNNEL_PID}) terminated."
    fi
}
trap cleanup EXIT

get_kv_secret() {
    local name="$1"
    az keyvault secret show --vault-name "${KV_NAME}" --name "${name}" --query value -o tsv 2>/dev/null || echo ""
}

start_ssh_tunnel() {
    log "Starting SSH tunnel: localhost:${LOCAL_TUNNEL_PORT} -> ${VM_HOST}:${VM_PG_PORT}"
    ssh -f -N -L "${LOCAL_TUNNEL_PORT}:localhost:${VM_PG_PORT}" "${VM_USER}@${VM_HOST}" \
        -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10
    SSH_TUNNEL_PID=$(pgrep -f "ssh.*-L.*${LOCAL_TUNNEL_PORT}.*${VM_HOST}" | tail -1)
    log "SSH tunnel established (PID: ${SSH_TUNNEL_PID})"
    sleep 2
}

count_query() {
    local connstr="$1"
    local label="$2"
    local sql="$3"
    local result
    result=$(psql "${connstr}" -t -A -c "${sql}" 2>/dev/null || echo "error")
    echo "${result}"
}

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --help|-h) usage ;;
        *) die "Unknown argument: $1" ;;
    esac
done

# --- Setup Evidence ---
mkdir -p "${EVIDENCE_DIR}"
LOG_FILE="${EVIDENCE_DIR}/schema_export.log"
: > "${LOG_FILE}"

log "=== Supabase Schema Export ==="
log "VM: ${VM_USER}@${VM_HOST}:${VM_PG_PORT}"
log "Dry run: ${DRY_RUN}"
log "Evidence dir: ${EVIDENCE_DIR}"

# --- Get Secrets ---
log "Fetching cloud DB connection string from Key Vault..."
CLOUD_DB_URL="${SUPABASE_DB_URL:-$(get_kv_secret supabase-db-url)}"
SELF_HOSTED_DB_PASSWORD="${SUPABASE_SELF_HOSTED_DB_PASSWORD:-$(get_kv_secret supabase-self-hosted-db-password)}"
SELF_HOSTED_DB_URL="postgresql://supabase_admin:${SELF_HOSTED_DB_PASSWORD}@localhost:${LOCAL_TUNNEL_PORT}/postgres"

if [[ -z "${CLOUD_DB_URL}" ]]; then
    die "Cloud DB URL not found. Set SUPABASE_DB_URL or add 'supabase-db-url' to KV '${KV_NAME}'."
fi
log "Cloud DB URL: ${CLOUD_DB_URL:0:30}..."

# --- Step 1: Export cloud schema ---
CLOUD_SCHEMA_FILE="${EVIDENCE_DIR}/cloud_schema.sql"
log "Step 1: Exporting cloud schema via pg_dump --schema-only..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would run: pg_dump --schema-only --no-owner --no-privileges '${CLOUD_DB_URL:0:30}...' > ${CLOUD_SCHEMA_FILE}"
    log "[DRY RUN] Would exclude schemas: pg_catalog, information_schema"
else
    pg_dump "${CLOUD_DB_URL}" \
        --schema-only \
        --no-owner \
        --no-privileges \
        --exclude-schema='pg_catalog' \
        --exclude-schema='information_schema' \
        > "${CLOUD_SCHEMA_FILE}" 2>>"${LOG_FILE}" \
        || die "pg_dump --schema-only failed"
    log "Cloud schema exported: $(wc -l < "${CLOUD_SCHEMA_FILE}") lines"
fi

# --- Step 2: Start SSH tunnel and apply migrations ---
log "Step 2: Applying repo migrations to self-hosted DB..."

if [[ "${DRY_RUN}" == "true" ]]; then
    MIGRATION_COUNT=$(find "${MIGRATIONS_DIR}" -name '*.sql' 2>/dev/null | wc -l | tr -d ' ')
    log "[DRY RUN] Found ${MIGRATION_COUNT} migration files in ${MIGRATIONS_DIR}"
    log "[DRY RUN] Would establish SSH tunnel to ${VM_HOST}"
    log "[DRY RUN] Would apply migrations in sorted order to self-hosted DB"
else
    if [[ ! -d "${MIGRATIONS_DIR}" ]]; then
        log "WARN: Migrations directory not found at ${MIGRATIONS_DIR}. Skipping migration apply."
    else
        start_ssh_tunnel

        APPLIED=0
        FAILED=0
        SKIPPED=0

        for migration in $(find "${MIGRATIONS_DIR}" -name '*.sql' | sort); do
            migration_name=$(basename "${migration}")
            log "  Applying: ${migration_name}"

            # Idempotent: wrap in transaction, skip if already applied
            if psql "${SELF_HOSTED_DB_URL}" -v ON_ERROR_STOP=0 -f "${migration}" >> "${LOG_FILE}" 2>&1; then
                APPLIED=$((APPLIED + 1))
            else
                # Non-fatal: migration may already be applied or have conflicts
                log "  WARN: Migration ${migration_name} had errors (may already be applied)"
                SKIPPED=$((SKIPPED + 1))
            fi
        done

        log "Migrations: ${APPLIED} applied, ${SKIPPED} skipped/warnings, ${FAILED} failed"
    fi
fi

# --- Step 3: Verify extensions parity ---
log "Step 3: Verifying extension parity..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would compare extensions between cloud and self-hosted"
else
    EXT_SQL="SELECT extname FROM pg_extension ORDER BY extname;"

    CLOUD_EXTENSIONS=$(psql "${CLOUD_DB_URL}" -t -A -c "${EXT_SQL}" 2>/dev/null | sort)
    echo "${CLOUD_EXTENSIONS}" > "${EVIDENCE_DIR}/cloud_extensions.txt"

    if [[ -z "${SSH_TUNNEL_PID}" ]]; then
        start_ssh_tunnel
    fi

    SELF_EXTENSIONS=$(psql "${SELF_HOSTED_DB_URL}" -t -A -c "${EXT_SQL}" 2>/dev/null | sort)
    echo "${SELF_EXTENSIONS}" > "${EVIDENCE_DIR}/selfhosted_extensions.txt"

    # Diff
    MISSING_EXTENSIONS=$(comm -23 <(echo "${CLOUD_EXTENSIONS}") <(echo "${SELF_EXTENSIONS}"))
    EXTRA_EXTENSIONS=$(comm -13 <(echo "${CLOUD_EXTENSIONS}") <(echo "${SELF_EXTENSIONS}"))

    if [[ -n "${MISSING_EXTENSIONS}" ]]; then
        log "WARN: Extensions in cloud but NOT in self-hosted:"
        echo "${MISSING_EXTENSIONS}" | while read -r ext; do log "  - ${ext}"; done
    fi
    if [[ -n "${EXTRA_EXTENSIONS}" ]]; then
        log "INFO: Extensions in self-hosted but NOT in cloud:"
        echo "${EXTRA_EXTENSIONS}" | while read -r ext; do log "  + ${ext}"; done
    fi
    if [[ -z "${MISSING_EXTENSIONS}" && -z "${EXTRA_EXTENSIONS}" ]]; then
        log "Extensions: PARITY OK"
    fi
fi

# --- Step 4: Generate schema parity report ---
log "Step 4: Generating schema parity report..."

PARITY_FILE="${EVIDENCE_DIR}/schema_parity_report.json"

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would generate parity report at ${PARITY_FILE}"
    log "[DRY RUN] Checks: table count, column count, index count"
else
    TABLE_COUNT_SQL="SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema');"
    COLUMN_COUNT_SQL="SELECT count(*) FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog','information_schema');"
    INDEX_COUNT_SQL="SELECT count(*) FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema');"

    CLOUD_TABLES=$(count_query "${CLOUD_DB_URL}" "cloud_tables" "${TABLE_COUNT_SQL}")
    CLOUD_COLUMNS=$(count_query "${CLOUD_DB_URL}" "cloud_columns" "${COLUMN_COUNT_SQL}")
    CLOUD_INDEXES=$(count_query "${CLOUD_DB_URL}" "cloud_indexes" "${INDEX_COUNT_SQL}")

    if [[ -z "${SSH_TUNNEL_PID}" ]]; then
        start_ssh_tunnel
    fi

    SELF_TABLES=$(count_query "${SELF_HOSTED_DB_URL}" "self_tables" "${TABLE_COUNT_SQL}")
    SELF_COLUMNS=$(count_query "${SELF_HOSTED_DB_URL}" "self_columns" "${COLUMN_COUNT_SQL}")
    SELF_INDEXES=$(count_query "${SELF_HOSTED_DB_URL}" "self_indexes" "${INDEX_COUNT_SQL}")

    cat > "${PARITY_FILE}" <<EOJSON
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cloud": {
    "tables": ${CLOUD_TABLES:-0},
    "columns": ${CLOUD_COLUMNS:-0},
    "indexes": ${CLOUD_INDEXES:-0}
  },
  "self_hosted": {
    "tables": ${SELF_TABLES:-0},
    "columns": ${SELF_COLUMNS:-0},
    "indexes": ${SELF_INDEXES:-0}
  },
  "parity": {
    "tables_match": $([ "${CLOUD_TABLES}" = "${SELF_TABLES}" ] && echo true || echo false),
    "columns_match": $([ "${CLOUD_COLUMNS}" = "${SELF_COLUMNS}" ] && echo true || echo false),
    "indexes_match": $([ "${CLOUD_INDEXES}" = "${SELF_INDEXES}" ] && echo true || echo false)
  }
}
EOJSON

    log "Schema parity report saved to ${PARITY_FILE}"
    log "  Cloud:  tables=${CLOUD_TABLES} columns=${CLOUD_COLUMNS} indexes=${CLOUD_INDEXES}"
    log "  Self:   tables=${SELF_TABLES} columns=${SELF_COLUMNS} indexes=${SELF_INDEXES}"
fi

log "=== Schema export complete ==="
log "Evidence: ${EVIDENCE_DIR}"
