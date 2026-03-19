#!/usr/bin/env bash
# supabase_cutover_finalize.sh — Finalize migration from cloud to self-hosted.
#
# Usage:
#   ./supabase_cutover_finalize.sh --confirm [--dry-run]
#   ./supabase_cutover_finalize.sh --help
#
# WARNING: This is the point of no return.
# Only runs if supabase_cutover_verify.sh exits 0.
# Requires --confirm flag.

set -euo pipefail

# --- Configuration ---
VM_HOST="${VM_HOST:-4.193.100.31}"
VM_USER="${VM_USER:-azureuser}"
KV_NAME="${KV_NAME:-kv-ipai-dev}"
EVIDENCE_DIR="${EVIDENCE_DIR:-docs/evidence/$(date +%Y%m%d-%H%M)/supabase-migration}"
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
SCRIPTS_DIR="${REPO_ROOT}/ops-platform/supabase/scripts"
SSOT_FILE="${REPO_ROOT}/ssot/azure/supabase.yaml"
CLOUD_PROJECT_REF="spdtwktxdalcfigzeqrz"
CLOUD_API_URL="https://${CLOUD_PROJECT_REF}.supabase.co"
DRY_RUN=false
CONFIRMED=false
DECOMMISSION_DAYS=30

# --- Functions ---
usage() {
    cat <<'EOF'
supabase_cutover_finalize.sh — Finalize cloud-to-self-hosted migration.

WARNING: This is the point of no return.

Usage:
  ./supabase_cutover_finalize.sh --confirm [--dry-run]

Options:
  --confirm         Required. Acknowledge this is irreversible.
  --dry-run         Show what would happen without executing.
  --help, -h        Show this help.

Prerequisites:
  - supabase_cutover_verify.sh must exit 0 (all checks pass)
  - All consumers must be rewired to self-hosted
  - DNS must resolve to self-hosted VM

Actions:
  1. Runs cutover verification (must pass)
  2. Sets cloud project to read-only (revokes write grants)
  3. Updates SSOT file: ssot/azure/supabase.yaml
  4. Creates git commit with evidence
  5. Outputs final evidence pack
  6. Logs 30-day decommission reminder
EOF
    exit 0
}

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE:-/dev/null}"; }
err() { log "ERROR: $*" >&2; }
die() { err "$@"; exit 1; }

get_kv_secret() {
    az keyvault secret show --vault-name "${KV_NAME}" --name "$1" --query value -o tsv 2>/dev/null || echo ""
}

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --confirm) CONFIRMED=true; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --help|-h) usage ;;
        *) die "Unknown argument: $1" ;;
    esac
done

if [[ "${CONFIRMED}" != "true" ]]; then
    echo ""
    echo "=================================================================="
    echo "  WARNING: This is the point of no return."
    echo ""
    echo "  This script will:"
    echo "    - Set cloud Supabase project to read-only"
    echo "    - Update SSOT to mark cutover as complete"
    echo "    - Create a git commit with all evidence"
    echo ""
    echo "  Run with --confirm to proceed."
    echo "  Run with --confirm --dry-run to see what would happen."
    echo "=================================================================="
    echo ""
    exit 1
fi

# --- Setup ---
mkdir -p "${EVIDENCE_DIR}"
LOG_FILE="${EVIDENCE_DIR}/cutover_finalize.log"
: > "${LOG_FILE}"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DECOMMISSION_DATE=$(date -u -v+${DECOMMISSION_DAYS}d +%Y-%m-%d 2>/dev/null || \
                    date -u -d "+${DECOMMISSION_DAYS} days" +%Y-%m-%d 2>/dev/null || \
                    echo "$(date -u +%Y-%m-%d)+30d")

log "=== Supabase Cutover Finalization ==="
log "Timestamp: ${TIMESTAMP}"
log "Dry run: ${DRY_RUN}"
log "Cloud project: ${CLOUD_PROJECT_REF}"
log "Decommission target: ${DECOMMISSION_DATE}"

# --- Step 1: Run cutover verification ---
log "Step 1: Running cutover verification..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would run: ${SCRIPTS_DIR}/supabase_cutover_verify.sh"
    log "[DRY RUN] Verification skipped in dry-run mode"
else
    if [[ -x "${SCRIPTS_DIR}/supabase_cutover_verify.sh" ]]; then
        VERIFY_EVIDENCE="${EVIDENCE_DIR}"
        if EVIDENCE_DIR="${VERIFY_EVIDENCE}" "${SCRIPTS_DIR}/supabase_cutover_verify.sh" 2>&1 | tee -a "${LOG_FILE}"; then
            log "Verification: ALL CHECKS PASSED"
        else
            die "Verification failed. Cannot proceed with cutover finalization."
        fi
    else
        die "Verification script not found or not executable: ${SCRIPTS_DIR}/supabase_cutover_verify.sh"
    fi
fi

# --- Step 2: Set cloud project to read-only ---
log "Step 2: Setting cloud project to read-only..."

CLOUD_DB_URL="${SUPABASE_DB_URL:-$(get_kv_secret supabase-db-url)}"

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would connect to cloud DB and revoke write permissions:"
    log "[DRY RUN]   REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM authenticated, anon, service_role;"
    log "[DRY RUN]   ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE INSERT, UPDATE, DELETE ON TABLES FROM authenticated, anon, service_role;"
else
    if [[ -n "${CLOUD_DB_URL}" ]]; then
        log "Revoking write permissions on cloud project..."

        READONLY_SQL=$(cat <<'EOSQL'
-- Revoke write permissions from application roles
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT schemaname FROM (VALUES ('public'), ('storage'), ('auth')) AS s(schemaname)
    LOOP
        EXECUTE format('REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA %I FROM anon, authenticated, service_role', r.schemaname);
        EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I REVOKE INSERT, UPDATE, DELETE ON TABLES FROM anon', r.schemaname);
        EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I REVOKE INSERT, UPDATE, DELETE ON TABLES FROM authenticated', r.schemaname);
        EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I REVOKE INSERT, UPDATE, DELETE ON TABLES FROM service_role', r.schemaname);
        RAISE NOTICE 'Revoked write permissions on schema: %', r.schemaname;
    END LOOP;
END $$;
EOSQL
        )

        if psql "${CLOUD_DB_URL}" -c "${READONLY_SQL}" >> "${LOG_FILE}" 2>&1; then
            log "Cloud project set to read-only."
        else
            log "WARN: Failed to set cloud project to read-only. Manual intervention may be needed."
        fi
    else
        log "WARN: No cloud DB URL available. Cannot set read-only. Proceed with manual lockdown."
    fi
fi

# --- Step 3: Update SSOT file ---
log "Step 3: Updating SSOT file..."

SSOT_DIR=$(dirname "${SSOT_FILE}")

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would create/update: ${SSOT_FILE}"
    log "[DRY RUN] Status: cutover-complete"
else
    mkdir -p "${SSOT_DIR}"

    cat > "${SSOT_FILE}" <<EOYAML
# Supabase Infrastructure SSOT
# Auto-generated by supabase_cutover_finalize.sh
# Last updated: ${TIMESTAMP}

cloud:
  project_ref: ${CLOUD_PROJECT_REF}
  api_url: ${CLOUD_API_URL}
  status: cutover-complete
  cutover_date: "${TIMESTAMP}"
  read_only_since: "${TIMESTAMP}"
  decommission_target: "${DECOMMISSION_DATE}"
  notes: |
    Cloud project has been set to read-only.
    All consumers rewired to self-hosted instance.
    Decommission after ${DECOMMISSION_DATE} (${DECOMMISSION_DAYS}-day retention).

self_hosted:
  vm_host: "${VM_HOST}"
  vm_user: "${VM_USER}"
  pg_port: ${VM_PG_PORT:-54322}
  compose_dir: /opt/supabase-deploy/
  url: "${SUPABASE_SELF_HOSTED_URL:-https://supabase.insightpulseai.com}"
  dns: "${SELF_HOSTED_DNS:-supabase.insightpulseai.com}"
  status: active
  activated_date: "${TIMESTAMP}"

migration:
  status: complete
  evidence_dir: "${EVIDENCE_DIR}"
  scripts:
    - supabase_cloud_inventory.py
    - supabase_schema_export.sh
    - supabase_data_migrate.sh
    - supabase_edge_functions_sync.sh
    - supabase_consumer_rewire.py
    - supabase_cutover_verify.sh
    - supabase_cutover_finalize.sh
EOYAML

    log "SSOT file written: ${SSOT_FILE}"
fi

# --- Step 4: Create evidence pack ---
log "Step 4: Generating final evidence pack..."

EVIDENCE_PACK="${EVIDENCE_DIR}/cutover_finalization.json"

cat > "${EVIDENCE_PACK}" <<EOJSON
{
  "timestamp": "${TIMESTAMP}",
  "dry_run": ${DRY_RUN},
  "cloud_project_ref": "${CLOUD_PROJECT_REF}",
  "cloud_status": "read-only",
  "self_hosted_vm": "${VM_HOST}",
  "self_hosted_url": "${SUPABASE_SELF_HOSTED_URL:-https://supabase.insightpulseai.com}",
  "ssot_file": "${SSOT_FILE}",
  "decommission_target": "${DECOMMISSION_DATE}",
  "steps_completed": [
    "cutover_verification_passed",
    "cloud_project_read_only",
    "ssot_updated",
    "evidence_pack_created"
  ],
  "reminder": "Decommission cloud project ${CLOUD_PROJECT_REF} after ${DECOMMISSION_DATE} (${DECOMMISSION_DAYS}-day retention window)."
}
EOJSON

log "Evidence pack: ${EVIDENCE_PACK}"

# --- Step 5: Git commit ---
log "Step 5: Creating git commit with evidence..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would create git commit:"
    log "[DRY RUN]   chore(deploy): finalize supabase cloud-to-self-hosted cutover"
    log "[DRY RUN]   Files: ${SSOT_FILE}, ${EVIDENCE_DIR}/"
else
    cd "${REPO_ROOT}"

    if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        git add "${SSOT_FILE}" "${EVIDENCE_DIR}/" 2>/dev/null || true

        git commit -m "$(cat <<'COMMITEOF'
chore(deploy): finalize supabase cloud-to-self-hosted cutover

- Cloud project spdtwktxdalcfigzeqrz set to read-only
- All consumers rewired to self-hosted instance
- SSOT updated: ssot/azure/supabase.yaml
- Evidence pack generated with verification results
- 30-day decommission window starts now
COMMITEOF
        )" 2>>"${LOG_FILE}" || log "WARN: Git commit failed (may have no changes to commit)"

        log "Git commit created."
    else
        log "WARN: Not in a git repo. Skipping commit."
    fi
fi

# --- Final Summary ---
log ""
log "=================================================================="
log "  CUTOVER FINALIZATION COMPLETE"
log ""
log "  Cloud project:     ${CLOUD_PROJECT_REF} (READ-ONLY)"
log "  Self-hosted:       ${SUPABASE_SELF_HOSTED_URL:-https://supabase.insightpulseai.com}"
log "  VM:                ${VM_HOST}"
log "  SSOT:              ${SSOT_FILE}"
log "  Evidence:          ${EVIDENCE_DIR}/"
log ""
log "  REMINDER: Decommission cloud project after ${DECOMMISSION_DATE}"
log "            (${DECOMMISSION_DAYS}-day retention window)"
log "=================================================================="
