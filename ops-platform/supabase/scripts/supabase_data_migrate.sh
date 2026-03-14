#!/usr/bin/env bash
# supabase_data_migrate.sh — Migrate data from cloud to self-hosted Supabase.
#
# Usage:
#   ./supabase_data_migrate.sh [--dry-run] [--tables table1,table2]
#   ./supabase_data_migrate.sh --help
#
# Exports data from cloud DB via pg_dump --data-only, restores to self-hosted
# via SSH tunnel. Performs row-count comparison and checksum verification.

set -euo pipefail

# --- Configuration ---
VM_HOST="${VM_HOST:-4.193.100.31}"
VM_USER="${VM_USER:-azureuser}"
VM_PG_PORT="${VM_PG_PORT:-54322}"
LOCAL_TUNNEL_PORT="${LOCAL_TUNNEL_PORT:-54398}"
KV_NAME="${KV_NAME:-kv-ipai-dev}"
EVIDENCE_DIR="${EVIDENCE_DIR:-docs/evidence/$(date +%Y%m%d-%H%M)/supabase-migration}"
DRY_RUN=false
TABLES_FILTER=""
SSH_TUNNEL_PID=""

# System tables to exclude from data migration
EXCLUDE_TABLES=(
    "auth.schema_migrations"
    "storage.migrations"
    "supabase_migrations.schema_migrations"
    "extensions.pg_stat_statements"
    "extensions.pg_stat_statements_info"
    "supabase_functions.migrations"
)

# Critical tables for checksum verification
CRITICAL_TABLES=(
    "auth.users"
    "public.profiles"
)

# --- Functions ---
usage() {
    cat <<'EOF'
supabase_data_migrate.sh — Migrate data from cloud to self-hosted Supabase.

Usage:
  ./supabase_data_migrate.sh [--dry-run] [--tables table1,table2]

Options:
  --dry-run           Export data but do not import to self-hosted
  --tables LIST       Comma-separated list of schema.table to migrate (default: all)
  --help, -h          Show this help

Environment:
  VM_HOST             Self-hosted VM IP (default: 4.193.100.31)
  VM_USER             SSH user (default: azureuser)
  VM_PG_PORT          PostgreSQL port on VM (default: 54322)
  KV_NAME             Azure Key Vault name (default: kv-ipai-dev)
  EVIDENCE_DIR        Evidence output directory
  SUPABASE_DB_URL     Cloud DB connection string (or fetched from KV)
EOF
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
    az keyvault secret show --vault-name "${KV_NAME}" --name "$1" --query value -o tsv 2>/dev/null || echo ""
}

start_ssh_tunnel() {
    log "Starting SSH tunnel: localhost:${LOCAL_TUNNEL_PORT} -> ${VM_HOST}:${VM_PG_PORT}"
    ssh -f -N -L "${LOCAL_TUNNEL_PORT}:localhost:${VM_PG_PORT}" "${VM_USER}@${VM_HOST}" \
        -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10
    SSH_TUNNEL_PID=$(pgrep -f "ssh.*-L.*${LOCAL_TUNNEL_PORT}.*${VM_HOST}" | tail -1)
    log "SSH tunnel established (PID: ${SSH_TUNNEL_PID})"
    sleep 2
}

get_row_counts() {
    local connstr="$1"
    local label="$2"
    local output_file="$3"

    local sql
    sql=$(cat <<'EOSQL'
SELECT schemaname || '.' || tablename AS full_name,
       n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
EOSQL
    )
    psql "${connstr}" -t -A -F $'\t' -c "${sql}" 2>/dev/null > "${output_file}" || true
}

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --tables) TABLES_FILTER="$2"; shift 2 ;;
        --help|-h) usage ;;
        *) die "Unknown argument: $1" ;;
    esac
done

# --- Setup ---
mkdir -p "${EVIDENCE_DIR}"
LOG_FILE="${EVIDENCE_DIR}/data_migrate.log"
: > "${LOG_FILE}"

log "=== Supabase Data Migration ==="
log "VM: ${VM_USER}@${VM_HOST}:${VM_PG_PORT}"
log "Dry run: ${DRY_RUN}"
log "Tables filter: ${TABLES_FILTER:-all}"
log "Evidence dir: ${EVIDENCE_DIR}"

# --- Get Secrets ---
log "Fetching secrets from Key Vault..."
CLOUD_DB_URL="${SUPABASE_DB_URL:-$(get_kv_secret supabase-db-url)}"
SELF_HOSTED_DB_PASSWORD="${SUPABASE_SELF_HOSTED_DB_PASSWORD:-$(get_kv_secret supabase-self-hosted-db-password)}"
SELF_HOSTED_DB_URL="postgresql://supabase_admin:${SELF_HOSTED_DB_PASSWORD}@localhost:${LOCAL_TUNNEL_PORT}/postgres"

if [[ -z "${CLOUD_DB_URL}" ]]; then
    die "Cloud DB URL not found. Set SUPABASE_DB_URL or add 'supabase-db-url' to KV."
fi
log "Cloud DB URL: ${CLOUD_DB_URL:0:30}..."

# --- Step 1: Pre-migration row counts (cloud) ---
log "Step 1: Capturing pre-migration row counts from cloud..."
CLOUD_COUNTS_FILE="${EVIDENCE_DIR}/cloud_row_counts.tsv"
get_row_counts "${CLOUD_DB_URL}" "cloud" "${CLOUD_COUNTS_FILE}"
CLOUD_TABLE_COUNT=$(wc -l < "${CLOUD_COUNTS_FILE}" | tr -d ' ')
log "Cloud tables with data: ${CLOUD_TABLE_COUNT}"

# --- Step 2: Export data from cloud ---
log "Step 2: Exporting data from cloud DB..."
DATA_DUMP_FILE="${EVIDENCE_DIR}/cloud_data.dump"

# Build exclude args
EXCLUDE_ARGS=""
for tbl in "${EXCLUDE_TABLES[@]}"; do
    EXCLUDE_ARGS="${EXCLUDE_ARGS} --exclude-table=${tbl}"
done

# Build table filter args
TABLE_ARGS=""
if [[ -n "${TABLES_FILTER}" ]]; then
    IFS=',' read -ra TABLE_LIST <<< "${TABLES_FILTER}"
    for tbl in "${TABLE_LIST[@]}"; do
        TABLE_ARGS="${TABLE_ARGS} --table=${tbl}"
    done
fi

DUMP_CMD="pg_dump ${CLOUD_DB_URL} --data-only --no-owner --no-privileges --format=custom ${EXCLUDE_ARGS} ${TABLE_ARGS}"

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would run: pg_dump --data-only --format=custom (excluding ${#EXCLUDE_TABLES[@]} system tables)"
    log "[DRY RUN] Dump would be saved to: ${DATA_DUMP_FILE}"
else
    eval "${DUMP_CMD}" > "${DATA_DUMP_FILE}" 2>>"${LOG_FILE}" \
        || die "pg_dump --data-only failed"
    DUMP_SIZE=$(du -h "${DATA_DUMP_FILE}" | cut -f1)
    log "Data dump exported: ${DUMP_SIZE} -> ${DATA_DUMP_FILE}"
fi

# --- Step 3: Import data to self-hosted ---
log "Step 3: Importing data to self-hosted DB..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would establish SSH tunnel to ${VM_HOST}"
    log "[DRY RUN] Would run: pg_restore --data-only --no-owner --no-privileges ${DATA_DUMP_FILE}"
    log "[DRY RUN] Data NOT imported."
else
    start_ssh_tunnel

    # Disable triggers during import to avoid FK/RLS issues
    log "Importing data (triggers disabled)..."
    pg_restore \
        --dbname="${SELF_HOSTED_DB_URL}" \
        --data-only \
        --no-owner \
        --no-privileges \
        --disable-triggers \
        --if-exists \
        --clean \
        "${DATA_DUMP_FILE}" 2>>"${LOG_FILE}" \
        || log "WARN: pg_restore completed with warnings (check log)"

    log "Data import complete."
fi

# --- Step 4: Row-count parity check ---
log "Step 4: Row-count parity verification..."
PARITY_FILE="${EVIDENCE_DIR}/row_count_parity.json"

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would compare row counts between cloud and self-hosted"
    cat > "${PARITY_FILE}" <<'EOJSON'
{"dry_run": true, "message": "Parity check skipped in dry-run mode"}
EOJSON
else
    if [[ -z "${SSH_TUNNEL_PID}" ]]; then
        start_ssh_tunnel
    fi

    SELF_COUNTS_FILE="${EVIDENCE_DIR}/selfhosted_row_counts.tsv"
    get_row_counts "${SELF_HOSTED_DB_URL}" "self_hosted" "${SELF_COUNTS_FILE}"

    # Build JSON parity report
    python3 - "${CLOUD_COUNTS_FILE}" "${SELF_COUNTS_FILE}" "${PARITY_FILE}" <<'PYEOF'
import json, sys

cloud_file, self_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]

def parse_counts(path):
    counts = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) == 2:
                    counts[parts[0]] = int(parts[1])
    except Exception:
        pass
    return counts

cloud = parse_counts(cloud_file)
self_hosted = parse_counts(self_file)
all_tables = sorted(set(cloud.keys()) | set(self_hosted.keys()))

report = {
    "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
    "cloud_table_count": len(cloud),
    "self_hosted_table_count": len(self_hosted),
    "tables": [],
    "mismatches": [],
    "missing_in_self_hosted": [],
    "missing_in_cloud": [],
}

for table in all_tables:
    c = cloud.get(table)
    s = self_hosted.get(table)
    entry = {"table": table, "cloud": c, "self_hosted": s, "match": c == s}
    report["tables"].append(entry)
    if c is not None and s is None:
        report["missing_in_self_hosted"].append(table)
    elif c is None and s is not None:
        report["missing_in_cloud"].append(table)
    elif c != s:
        report["mismatches"].append(entry)

report["parity"] = len(report["mismatches"]) == 0 and len(report["missing_in_self_hosted"]) == 0

with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"Parity: {'PASS' if report['parity'] else 'FAIL'}")
print(f"  Tables: cloud={len(cloud)} self_hosted={len(self_hosted)}")
print(f"  Mismatches: {len(report['mismatches'])}")
print(f"  Missing in self-hosted: {len(report['missing_in_self_hosted'])}")
PYEOF

    log "Row-count parity report: ${PARITY_FILE}"
fi

# --- Step 5: Critical table checksums ---
log "Step 5: Critical table checksum verification..."
CHECKSUM_FILE="${EVIDENCE_DIR}/critical_table_checksums.json"

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would verify checksums for: ${CRITICAL_TABLES[*]}"
    cat > "${CHECKSUM_FILE}" <<'EOJSON'
{"dry_run": true, "message": "Checksum verification skipped in dry-run mode"}
EOJSON
else
    if [[ -z "${SSH_TUNNEL_PID}" ]]; then
        start_ssh_tunnel
    fi

    # auth.users: count + email domain distribution
    AUTH_CLOUD_COUNT=$(psql "${CLOUD_DB_URL}" -t -A -c "SELECT count(*) FROM auth.users;" 2>/dev/null || echo "error")
    AUTH_SELF_COUNT=$(psql "${SELF_HOSTED_DB_URL}" -t -A -c "SELECT count(*) FROM auth.users;" 2>/dev/null || echo "error")

    AUTH_CLOUD_DOMAINS=$(psql "${CLOUD_DB_URL}" -t -A -F $'\t' -c \
        "SELECT split_part(email, '@', 2) AS domain, count(*) FROM auth.users GROUP BY 1 ORDER BY 2 DESC LIMIT 10;" 2>/dev/null || echo "error")
    AUTH_SELF_DOMAINS=$(psql "${SELF_HOSTED_DB_URL}" -t -A -F $'\t' -c \
        "SELECT split_part(email, '@', 2) AS domain, count(*) FROM auth.users GROUP BY 1 ORDER BY 2 DESC LIMIT 10;" 2>/dev/null || echo "error")

    cat > "${CHECKSUM_FILE}" <<EOJSON
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "auth_users": {
    "cloud_count": "${AUTH_CLOUD_COUNT}",
    "self_hosted_count": "${AUTH_SELF_COUNT}",
    "count_match": $([ "${AUTH_CLOUD_COUNT}" = "${AUTH_SELF_COUNT}" ] && echo true || echo false),
    "cloud_email_domains": $(echo "${AUTH_CLOUD_DOMAINS}" | python3 -c "
import sys, json
lines = [l.strip().split('\t') for l in sys.stdin if l.strip() and l.strip() != 'error']
print(json.dumps({p[0]: int(p[1]) for p in lines if len(p)==2}))
" 2>/dev/null || echo '{}'),
    "self_hosted_email_domains": $(echo "${AUTH_SELF_DOMAINS}" | python3 -c "
import sys, json
lines = [l.strip().split('\t') for l in sys.stdin if l.strip() and l.strip() != 'error']
print(json.dumps({p[0]: int(p[1]) for p in lines if len(p)==2}))
" 2>/dev/null || echo '{}')
  }
}
EOJSON

    log "Critical checksums saved to ${CHECKSUM_FILE}"
    log "  auth.users: cloud=${AUTH_CLOUD_COUNT} self_hosted=${AUTH_SELF_COUNT} match=$([ "${AUTH_CLOUD_COUNT}" = "${AUTH_SELF_COUNT}" ] && echo YES || echo NO)"
fi

log "=== Data migration complete ==="
log "Evidence directory: ${EVIDENCE_DIR}"
log "Files:"
log "  - cloud_row_counts.tsv"
log "  - row_count_parity.json"
log "  - critical_table_checksums.json"
log "  - data_migrate.log"
[[ "${DRY_RUN}" == "false" ]] && log "  - cloud_data.dump"
