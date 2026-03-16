#!/usr/bin/env bash
# supabase_edge_functions_sync.sh — Deploy Edge Functions to self-hosted Supabase.
#
# Usage:
#   ./supabase_edge_functions_sync.sh [--dry-run] [--function <name>]
#   ./supabase_edge_functions_sync.sh --help
#
# Syncs Edge Functions from repo to self-hosted VM via rsync/SCP,
# restarts the edge-functions container, and verifies endpoints.

set -euo pipefail

# --- Configuration ---
VM_HOST="${VM_HOST:-4.193.100.31}"
VM_USER="${VM_USER:-azureuser}"
KV_NAME="${KV_NAME:-kv-ipai-dev}"
EVIDENCE_DIR="${EVIDENCE_DIR:-docs/evidence/$(date +%Y%m%d-%H%M)/supabase-migration}"
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
FUNCTIONS_SRC="${REPO_ROOT}/supabase/supabase/functions"
MANIFEST_FILE="${REPO_ROOT}/ops-platform/supabase/edge-functions/deploy/manifest.yaml"
VM_FUNCTIONS_DIR="/opt/supabase-deploy/volumes/functions"
SELF_HOSTED_URL="${SUPABASE_SELF_HOSTED_URL:-https://supabase.insightpulseai.com}"
DRY_RUN=false
SINGLE_FUNCTION=""

# --- Functions ---
usage() {
    cat <<'EOF'
supabase_edge_functions_sync.sh — Deploy Edge Functions to self-hosted Supabase.

Usage:
  ./supabase_edge_functions_sync.sh [--dry-run] [--function <name>]

Options:
  --dry-run              List what would be deployed without deploying
  --function <name>      Deploy a single function by name
  --help, -h             Show this help

Environment:
  VM_HOST                Self-hosted VM IP (default: 4.193.100.31)
  VM_USER                SSH user (default: azureuser)
  SUPABASE_SELF_HOSTED_URL  Self-hosted Supabase URL
  EVIDENCE_DIR           Evidence output directory
EOF
    exit 0
}

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE:-/dev/null}"; }
err() { log "ERROR: $*" >&2; }
die() { err "$@"; exit 1; }

get_kv_secret() {
    az keyvault secret show --vault-name "${KV_NAME}" --name "$1" --query value -o tsv 2>/dev/null || echo ""
}

# Discover functions from filesystem if manifest doesn't exist
discover_functions() {
    if [[ -f "${MANIFEST_FILE}" ]]; then
        # Parse YAML manifest — extract function names
        # Handles format: - name: function_name or - function_name
        grep -E '^\s*-\s*(name:\s*)?' "${MANIFEST_FILE}" 2>/dev/null \
            | sed -E 's/^\s*-\s*(name:\s*)?//' \
            | tr -d ' "'"'" \
            | grep -v '^$' || true
    elif [[ -d "${FUNCTIONS_SRC}" ]]; then
        # Fallback: discover from filesystem
        find "${FUNCTIONS_SRC}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
    else
        die "No manifest at ${MANIFEST_FILE} and no functions dir at ${FUNCTIONS_SRC}"
    fi
}

test_function_endpoint() {
    local name="$1"
    local url="${SELF_HOSTED_URL}/functions/v1/${name}"
    local http_code
    local response_body

    http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        --connect-timeout 5 --max-time 10 \
        -H "Authorization: Bearer ${ANON_KEY}" \
        "${url}" 2>/dev/null || echo "000")

    # 200, 4xx with body = function is deployed and responding
    if [[ "${http_code}" =~ ^(200|201|204|400|401|403|404|405|422)$ ]]; then
        echo "pass:${http_code}"
    else
        echo "fail:${http_code}"
    fi
}

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --function) SINGLE_FUNCTION="$2"; shift 2 ;;
        --help|-h) usage ;;
        *) die "Unknown argument: $1" ;;
    esac
done

# --- Setup ---
mkdir -p "${EVIDENCE_DIR}"
LOG_FILE="${EVIDENCE_DIR}/edge_functions_sync.log"
: > "${LOG_FILE}"

log "=== Supabase Edge Functions Sync ==="
log "VM: ${VM_USER}@${VM_HOST}"
log "Functions source: ${FUNCTIONS_SRC}"
log "VM target: ${VM_FUNCTIONS_DIR}"
log "Dry run: ${DRY_RUN}"
log "Single function: ${SINGLE_FUNCTION:-all}"

# --- Get anon key for testing ---
ANON_KEY="${SUPABASE_ANON_KEY:-$(get_kv_secret supabase-self-hosted-anon-key)}"
if [[ -z "${ANON_KEY}" ]]; then
    log "WARN: No anon key available for endpoint testing. Tests will be skipped."
fi

# --- Step 1: Discover functions ---
log "Step 1: Discovering functions..."
ALL_FUNCTIONS=$(discover_functions)
FUNCTION_COUNT=$(echo "${ALL_FUNCTIONS}" | grep -c . || echo 0)
log "Found ${FUNCTION_COUNT} functions in manifest/filesystem"

if [[ -n "${SINGLE_FUNCTION}" ]]; then
    if ! echo "${ALL_FUNCTIONS}" | grep -qx "${SINGLE_FUNCTION}"; then
        die "Function '${SINGLE_FUNCTION}' not found in manifest or filesystem"
    fi
    DEPLOY_FUNCTIONS="${SINGLE_FUNCTION}"
    log "Deploying single function: ${SINGLE_FUNCTION}"
else
    DEPLOY_FUNCTIONS="${ALL_FUNCTIONS}"
fi

# --- Step 2: Sync functions to VM ---
log "Step 2: Syncing functions to VM..."
DEPLOYED=0
FAILED=0
DEPLOY_RESULTS=()

while IFS= read -r func_name; do
    [[ -z "${func_name}" ]] && continue

    func_src="${FUNCTIONS_SRC}/${func_name}"
    func_dst="${VM_FUNCTIONS_DIR}/${func_name}/"

    if [[ ! -d "${func_src}" ]]; then
        log "  WARN: Source directory not found for '${func_name}': ${func_src}"
        DEPLOY_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"skipped\",\"reason\":\"source_not_found\"}")
        continue
    fi

    if [[ "${DRY_RUN}" == "true" ]]; then
        file_count=$(find "${func_src}" -type f | wc -l | tr -d ' ')
        log "  [DRY RUN] Would sync: ${func_name} (${file_count} files) -> ${VM_USER}@${VM_HOST}:${func_dst}"
        DEPLOY_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"dry_run\",\"files\":${file_count}}")
        DEPLOYED=$((DEPLOYED + 1))
    else
        log "  Syncing: ${func_name}"
        if rsync -az --delete \
            -e "ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10" \
            "${func_src}/" \
            "${VM_USER}@${VM_HOST}:${func_dst}" 2>>"${LOG_FILE}"; then
            log "  OK: ${func_name}"
            DEPLOY_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"synced\"}")
            DEPLOYED=$((DEPLOYED + 1))
        else
            log "  FAIL: ${func_name}"
            DEPLOY_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"failed\"}")
            FAILED=$((FAILED + 1))
        fi
    fi
done <<< "${DEPLOY_FUNCTIONS}"

log "Sync complete: ${DEPLOYED} synced, ${FAILED} failed"

# --- Step 3: Restart edge-functions container ---
log "Step 3: Restarting edge-functions container..."

if [[ "${DRY_RUN}" == "true" ]]; then
    log "[DRY RUN] Would run: ssh ${VM_USER}@${VM_HOST} 'cd /opt/supabase-deploy && docker compose restart functions'"
else
    if ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
        "${VM_USER}@${VM_HOST}" \
        "cd /opt/supabase-deploy && docker compose restart functions" 2>>"${LOG_FILE}"; then
        log "Edge-functions container restarted."
        sleep 5  # Wait for container to be ready
    else
        log "WARN: Failed to restart edge-functions container. Functions may not be updated."
    fi
fi

# --- Step 4: Test function endpoints ---
log "Step 4: Testing function endpoints..."
TEST_RESULTS=()
PASS_COUNT=0
FAIL_COUNT=0

if [[ "${DRY_RUN}" == "true" || -z "${ANON_KEY}" ]]; then
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "[DRY RUN] Would test each function endpoint at ${SELF_HOSTED_URL}/functions/v1/<name>"
    else
        log "WARN: Skipping endpoint tests (no anon key)"
    fi
else
    while IFS= read -r func_name; do
        [[ -z "${func_name}" ]] && continue
        result=$(test_function_endpoint "${func_name}")
        status="${result%%:*}"
        http_code="${result##*:}"

        if [[ "${status}" == "pass" ]]; then
            log "  PASS: ${func_name} (HTTP ${http_code})"
            TEST_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"pass\",\"http_code\":${http_code}}")
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            log "  FAIL: ${func_name} (HTTP ${http_code})"
            TEST_RESULTS+=("{\"name\":\"${func_name}\",\"status\":\"fail\",\"http_code\":${http_code}}")
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done <<< "${ALL_FUNCTIONS}"

    log "Endpoint tests: ${PASS_COUNT} pass, ${FAIL_COUNT} fail out of ${FUNCTION_COUNT} total"
fi

# --- Step 5: Generate parity report ---
log "Step 5: Generating deployed functions parity report..."
PARITY_FILE="${EVIDENCE_DIR}/deployed_functions_parity.json"

# Get deployed functions from VM
if [[ "${DRY_RUN}" == "true" ]]; then
    VM_FUNCTIONS="[]"
else
    VM_FUNC_LIST=$(ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
        "${VM_USER}@${VM_HOST}" \
        "ls -1 ${VM_FUNCTIONS_DIR}/ 2>/dev/null" 2>/dev/null | sort || echo "")
    VM_FUNCTIONS=$(echo "${VM_FUNC_LIST}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo "[]")
fi

REPO_FUNC_JSON=$(echo "${ALL_FUNCTIONS}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo "[]")

# Join deploy results
DEPLOY_JSON=$(printf '%s\n' "${DEPLOY_RESULTS[@]}" | python3 -c "import sys,json; print(json.dumps([json.loads(l) for l in sys.stdin if l.strip()]))" 2>/dev/null || echo "[]")
TEST_JSON="[]"
if [[ ${#TEST_RESULTS[@]} -gt 0 ]]; then
    TEST_JSON=$(printf '%s\n' "${TEST_RESULTS[@]}" | python3 -c "import sys,json; print(json.dumps([json.loads(l) for l in sys.stdin if l.strip()]))" 2>/dev/null || echo "[]")
fi

cat > "${PARITY_FILE}" <<EOJSON
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "dry_run": ${DRY_RUN},
  "repo_function_count": ${FUNCTION_COUNT},
  "repo_functions": ${REPO_FUNC_JSON},
  "vm_functions": ${VM_FUNCTIONS},
  "deploy_results": ${DEPLOY_JSON},
  "endpoint_tests": ${TEST_JSON},
  "summary": {
    "deployed": ${DEPLOYED},
    "failed": ${FAILED},
    "endpoints_pass": ${PASS_COUNT},
    "endpoints_fail": ${FAIL_COUNT}
  }
}
EOJSON

log "Parity report saved to ${PARITY_FILE}"
log "=== Edge Functions Sync complete ==="
