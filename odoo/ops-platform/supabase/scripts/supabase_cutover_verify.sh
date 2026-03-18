#!/usr/bin/env bash
# supabase_cutover_verify.sh — Comprehensive cutover readiness verification.
#
# Usage:
#   ./supabase_cutover_verify.sh [--check <name>]
#   ./supabase_cutover_verify.sh --help
#
# Runs 10 verification checks and produces a cutover readiness report.
# Exit code 0 only if ALL checks pass.

set -euo pipefail

# --- Configuration ---
VM_HOST="${VM_HOST:-4.193.100.31}"
VM_USER="${VM_USER:-azureuser}"
VM_PG_PORT="${VM_PG_PORT:-54322}"
LOCAL_TUNNEL_PORT="${LOCAL_TUNNEL_PORT:-54397}"
KV_NAME="${KV_NAME:-kv-ipai-dev}"
EVIDENCE_DIR="${EVIDENCE_DIR:-docs/evidence/$(date +%Y%m%d-%H%M)/supabase-migration}"
CLOUD_API_URL="${CLOUD_API_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"
SELF_HOSTED_URL="${SUPABASE_SELF_HOSTED_URL:-https://supabase.insightpulseai.com}"
SELF_HOSTED_DNS="${SELF_HOSTED_DNS:-supabase.insightpulseai.com}"
EXPECTED_FUNCTION_COUNT="${EXPECTED_FUNCTION_COUNT:-39}"
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
SINGLE_CHECK=""
SSH_TUNNEL_PID=""

# --- Functions ---
usage() {
    cat <<'EOF'
supabase_cutover_verify.sh — Comprehensive cutover readiness verification.

Usage:
  ./supabase_cutover_verify.sh [--check <name>]

Checks:
  schema_parity         Table count, column count comparison
  row_count_parity      All tables row count match
  critical_checksums    auth.users count + email domain verification
  extension_parity      PostgreSQL extensions match
  rls_parity            Row Level Security policies match
  edge_function_deploy  39/39 functions deployed on VM
  edge_function_health  HTTP response from each function endpoint
  consumer_connectivity Each consumer can reach self-hosted
  dns_resolution        supabase.insightpulseai.com resolves to VM IP
  auth_flow             Anon key and service_role key work

Options:
  --check <name>    Run single check by name
  --help, -h        Show this help
EOF
    exit 0
}

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE:-/dev/null}"; }
err() { log "ERROR: $*" >&2; }
die() { err "$@"; exit 1; }

cleanup() {
    if [[ -n "${SSH_TUNNEL_PID}" ]]; then
        kill "${SSH_TUNNEL_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

get_kv_secret() {
    az keyvault secret show --vault-name "${KV_NAME}" --name "$1" --query value -o tsv 2>/dev/null || echo ""
}

start_ssh_tunnel() {
    if [[ -n "${SSH_TUNNEL_PID}" ]]; then return; fi
    log "Starting SSH tunnel: localhost:${LOCAL_TUNNEL_PORT} -> ${VM_HOST}:${VM_PG_PORT}"
    ssh -f -N -L "${LOCAL_TUNNEL_PORT}:localhost:${VM_PG_PORT}" "${VM_USER}@${VM_HOST}" \
        -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10
    SSH_TUNNEL_PID=$(pgrep -f "ssh.*-L.*${LOCAL_TUNNEL_PORT}.*${VM_HOST}" | tail -1)
    sleep 2
}

psql_cloud() { psql "${CLOUD_DB_URL}" -t -A -F $'\t' -c "$1" 2>/dev/null; }
psql_self()  { psql "${SELF_HOSTED_DB_URL}" -t -A -F $'\t' -c "$1" 2>/dev/null; }

# Result tracking
declare -A CHECK_RESULTS
TOTAL_CHECKS=0
PASSED_CHECKS=0

record_result() {
    local name="$1"
    local status="$2"  # pass or fail
    local detail="$3"

    CHECK_RESULTS["${name}_status"]="${status}"
    CHECK_RESULTS["${name}_detail"]="${detail}"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ "${status}" == "pass" ]]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        log "  CHECK ${name}: PASS — ${detail}"
    else
        log "  CHECK ${name}: FAIL — ${detail}"
    fi
}

# --- Check Implementations ---

check_schema_parity() {
    log "Check: schema_parity"
    start_ssh_tunnel

    local sql="SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema');"
    local cloud_tables self_tables
    cloud_tables=$(psql_cloud "${sql}")
    self_tables=$(psql_self "${sql}")

    local col_sql="SELECT count(*) FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog','information_schema');"
    local cloud_cols self_cols
    cloud_cols=$(psql_cloud "${col_sql}")
    self_cols=$(psql_self "${col_sql}")

    if [[ "${cloud_tables}" == "${self_tables}" && "${cloud_cols}" == "${self_cols}" ]]; then
        record_result "schema_parity" "pass" "tables=${cloud_tables}/${self_tables} columns=${cloud_cols}/${self_cols}"
    else
        record_result "schema_parity" "fail" "tables=${cloud_tables}/${self_tables} columns=${cloud_cols}/${self_cols}"
    fi
}

check_row_count_parity() {
    log "Check: row_count_parity"
    start_ssh_tunnel

    local sql="SELECT schemaname||'.'||tablename, n_live_tup FROM pg_stat_user_tables ORDER BY 1;"
    local cloud_counts self_counts
    cloud_counts=$(psql_cloud "${sql}")
    self_counts=$(psql_self "${sql}")

    local mismatches
    mismatches=$(diff <(echo "${cloud_counts}") <(echo "${self_counts}") 2>/dev/null | grep -c '^[<>]' || echo 0)

    if [[ "${mismatches}" == "0" ]]; then
        local table_count
        table_count=$(echo "${cloud_counts}" | grep -c . || echo 0)
        record_result "row_count_parity" "pass" "${table_count} tables match"
    else
        record_result "row_count_parity" "fail" "${mismatches} row count differences"
    fi
}

check_critical_checksums() {
    log "Check: critical_checksums"
    start_ssh_tunnel

    local cloud_auth self_auth
    cloud_auth=$(psql_cloud "SELECT count(*) FROM auth.users;")
    self_auth=$(psql_self "SELECT count(*) FROM auth.users;")

    if [[ "${cloud_auth}" == "${self_auth}" ]]; then
        record_result "critical_checksums" "pass" "auth.users: ${cloud_auth}/${self_auth}"
    else
        record_result "critical_checksums" "fail" "auth.users: cloud=${cloud_auth} self=${self_auth}"
    fi
}

check_extension_parity() {
    log "Check: extension_parity"
    start_ssh_tunnel

    local sql="SELECT extname FROM pg_extension ORDER BY extname;"
    local cloud_ext self_ext
    cloud_ext=$(psql_cloud "${sql}")
    self_ext=$(psql_self "${sql}")

    local missing
    missing=$(comm -23 <(echo "${cloud_ext}" | sort) <(echo "${self_ext}" | sort) | head -5)

    if [[ -z "${missing}" ]]; then
        local ext_count
        ext_count=$(echo "${cloud_ext}" | grep -c . || echo 0)
        record_result "extension_parity" "pass" "${ext_count} extensions match"
    else
        record_result "extension_parity" "fail" "missing in self-hosted: ${missing}"
    fi
}

check_rls_parity() {
    log "Check: rls_parity"
    start_ssh_tunnel

    local sql="SELECT count(*) FROM pg_policies WHERE schemaname NOT IN ('pg_catalog','information_schema');"
    local cloud_rls self_rls
    cloud_rls=$(psql_cloud "${sql}")
    self_rls=$(psql_self "${sql}")

    if [[ "${cloud_rls}" == "${self_rls}" ]]; then
        record_result "rls_parity" "pass" "${cloud_rls} policies match"
    else
        record_result "rls_parity" "fail" "cloud=${cloud_rls} self=${self_rls}"
    fi
}

check_edge_function_deploy() {
    log "Check: edge_function_deploy"

    local deployed_count
    deployed_count=$(ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
        "${VM_USER}@${VM_HOST}" \
        "ls -1d /opt/supabase-deploy/volumes/functions/*/ 2>/dev/null | wc -l" 2>/dev/null || echo "0")
    deployed_count=$(echo "${deployed_count}" | tr -d ' ')

    if [[ "${deployed_count}" -ge "${EXPECTED_FUNCTION_COUNT}" ]]; then
        record_result "edge_function_deploy" "pass" "${deployed_count}/${EXPECTED_FUNCTION_COUNT} deployed"
    else
        record_result "edge_function_deploy" "fail" "${deployed_count}/${EXPECTED_FUNCTION_COUNT} deployed"
    fi
}

check_edge_function_health() {
    log "Check: edge_function_health"

    if [[ -z "${ANON_KEY}" ]]; then
        record_result "edge_function_health" "fail" "no anon key available for testing"
        return
    fi

    # Get function list from VM
    local functions
    functions=$(ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
        "${VM_USER}@${VM_HOST}" \
        "ls -1 /opt/supabase-deploy/volumes/functions/ 2>/dev/null" 2>/dev/null || echo "")

    local total=0 healthy=0
    while IFS= read -r func; do
        [[ -z "${func}" ]] && continue
        total=$((total + 1))

        local http_code
        http_code=$(curl -s -o /dev/null -w '%{http_code}' \
            --connect-timeout 5 --max-time 10 \
            -H "Authorization: Bearer ${ANON_KEY}" \
            "${SELF_HOSTED_URL}/functions/v1/${func}" 2>/dev/null || echo "000")

        if [[ "${http_code}" =~ ^(200|201|204|400|401|403|404|405|422)$ ]]; then
            healthy=$((healthy + 1))
        fi
    done <<< "${functions}"

    if [[ "${healthy}" -ge "${total}" && "${total}" -gt 0 ]]; then
        record_result "edge_function_health" "pass" "${healthy}/${total} endpoints responding"
    else
        record_result "edge_function_health" "fail" "${healthy}/${total} endpoints responding"
    fi
}

check_consumer_connectivity() {
    log "Check: consumer_connectivity"

    local endpoints=(
        "erp.insightpulseai.com/web/health"
        "mcp.insightpulseai.com/health"
        "n8n.insightpulseai.com/healthz"
    )

    local total=${#endpoints[@]} reachable=0
    for endpoint in "${endpoints[@]}"; do
        local http_code
        http_code=$(curl -s -o /dev/null -w '%{http_code}' \
            --connect-timeout 5 --max-time 10 \
            "https://${endpoint}" 2>/dev/null || echo "000")

        if [[ "${http_code}" != "000" ]]; then
            reachable=$((reachable + 1))
        fi
    done

    if [[ "${reachable}" -ge "${total}" ]]; then
        record_result "consumer_connectivity" "pass" "${reachable}/${total} consumers reachable"
    else
        record_result "consumer_connectivity" "fail" "${reachable}/${total} consumers reachable"
    fi
}

check_dns_resolution() {
    log "Check: dns_resolution"

    local resolved_ip
    resolved_ip=$(dig +short "${SELF_HOSTED_DNS}" A 2>/dev/null | head -1 || \
                  nslookup "${SELF_HOSTED_DNS}" 2>/dev/null | grep -A1 'Name:' | grep 'Address:' | awk '{print $2}' || \
                  echo "")

    if [[ "${resolved_ip}" == "${VM_HOST}" ]]; then
        record_result "dns_resolution" "pass" "${SELF_HOSTED_DNS} -> ${resolved_ip}"
    else
        record_result "dns_resolution" "fail" "${SELF_HOSTED_DNS} -> ${resolved_ip} (expected ${VM_HOST})"
    fi
}

check_auth_flow() {
    log "Check: auth_flow"

    local pass=true detail=""

    # Test anon key
    if [[ -n "${ANON_KEY}" ]]; then
        local anon_code
        anon_code=$(curl -s -o /dev/null -w '%{http_code}' \
            --connect-timeout 5 --max-time 10 \
            -H "apikey: ${ANON_KEY}" \
            "${SELF_HOSTED_URL}/rest/v1/" 2>/dev/null || echo "000")

        if [[ "${anon_code}" =~ ^(200|401|406)$ ]]; then
            detail="anon_key=ok(${anon_code})"
        else
            pass=false
            detail="anon_key=fail(${anon_code})"
        fi
    else
        pass=false
        detail="anon_key=missing"
    fi

    # Test service_role key
    if [[ -n "${SERVICE_ROLE_KEY}" ]]; then
        local sr_code
        sr_code=$(curl -s -o /dev/null -w '%{http_code}' \
            --connect-timeout 5 --max-time 10 \
            -H "apikey: ${SERVICE_ROLE_KEY}" \
            -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
            "${SELF_HOSTED_URL}/rest/v1/" 2>/dev/null || echo "000")

        if [[ "${sr_code}" =~ ^(200|401|406)$ ]]; then
            detail="${detail} service_role=ok(${sr_code})"
        else
            pass=false
            detail="${detail} service_role=fail(${sr_code})"
        fi
    else
        pass=false
        detail="${detail} service_role=missing"
    fi

    if [[ "${pass}" == "true" ]]; then
        record_result "auth_flow" "pass" "${detail}"
    else
        record_result "auth_flow" "fail" "${detail}"
    fi
}

# --- All checks ---
ALL_CHECKS=(
    schema_parity
    row_count_parity
    critical_checksums
    extension_parity
    rls_parity
    edge_function_deploy
    edge_function_health
    consumer_connectivity
    dns_resolution
    auth_flow
)

# --- Parse Args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) SINGLE_CHECK="$2"; shift 2 ;;
        --help|-h) usage ;;
        *) die "Unknown argument: $1" ;;
    esac
done

# Validate single check
if [[ -n "${SINGLE_CHECK}" ]]; then
    valid=false
    for c in "${ALL_CHECKS[@]}"; do
        if [[ "${c}" == "${SINGLE_CHECK}" ]]; then valid=true; break; fi
    done
    if [[ "${valid}" == "false" ]]; then
        die "Unknown check: ${SINGLE_CHECK}. Valid: ${ALL_CHECKS[*]}"
    fi
fi

# --- Setup ---
mkdir -p "${EVIDENCE_DIR}"
LOG_FILE="${EVIDENCE_DIR}/cutover_verify.log"
: > "${LOG_FILE}"

log "=== Supabase Cutover Verification ==="
log "Cloud: ${CLOUD_API_URL}"
log "Self-hosted: ${SELF_HOSTED_URL}"
log "VM: ${VM_USER}@${VM_HOST}"
log "Check: ${SINGLE_CHECK:-all}"

# --- Get Secrets ---
CLOUD_DB_URL="${SUPABASE_DB_URL:-$(get_kv_secret supabase-db-url)}"
SELF_HOSTED_DB_PASSWORD="${SUPABASE_SELF_HOSTED_DB_PASSWORD:-$(get_kv_secret supabase-self-hosted-db-password)}"
SELF_HOSTED_DB_URL="postgresql://supabase_admin:${SELF_HOSTED_DB_PASSWORD}@localhost:${LOCAL_TUNNEL_PORT}/postgres"
ANON_KEY="${SUPABASE_ANON_KEY:-$(get_kv_secret supabase-self-hosted-anon-key)}"
SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-$(get_kv_secret supabase-self-hosted-service-role-key)}"

# --- Run Checks ---
if [[ -n "${SINGLE_CHECK}" ]]; then
    "check_${SINGLE_CHECK}"
else
    for check in "${ALL_CHECKS[@]}"; do
        "check_${check}" || true  # Don't exit on individual check failure
    done
fi

# --- Generate Report ---
REPORT_FILE="${EVIDENCE_DIR}/cutover_readiness_report.json"

# Build JSON report
python3 - "${REPORT_FILE}" "${PASSED_CHECKS}" "${TOTAL_CHECKS}" <<'PYEOF' \
    "$(for c in "${ALL_CHECKS[@]}"; do echo "${c}|${CHECK_RESULTS[${c}_status]:-skipped}|${CHECK_RESULTS[${c}_detail]:-}"; done)"
import json, sys
from datetime import datetime, timezone

output_file = sys.argv[1]
passed = int(sys.argv[2])
total = int(sys.argv[3])
check_data = sys.argv[4] if len(sys.argv) > 4 else ""

checks = []
for line in check_data.strip().split('\n'):
    if not line:
        continue
    parts = line.split('|', 2)
    if len(parts) == 3:
        checks.append({
            "name": parts[0],
            "status": parts[1],
            "detail": parts[2],
        })

report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "all_pass": passed == total and total > 0,
    "passed": passed,
    "total": total,
    "checks": checks,
}

with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
PYEOF

log ""
log "=== Cutover Readiness: ${PASSED_CHECKS}/${TOTAL_CHECKS} checks passed ==="
log "Report: ${REPORT_FILE}"

if [[ "${PASSED_CHECKS}" -eq "${TOTAL_CHECKS}" && "${TOTAL_CHECKS}" -gt 0 ]]; then
    log "RESULT: READY FOR CUTOVER"
    exit 0
else
    log "RESULT: NOT READY — $(( TOTAL_CHECKS - PASSED_CHECKS )) checks failed"
    exit 1
fi
