#!/usr/bin/env bash
# verify_stack.sh - Verify Odoo 19 CE + OCA stack installation
# Usage: ./scripts/stack/verify_stack.sh [--verbose] [--json]
#
# Runs comprehensive verification checks and outputs results.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EVIDENCE_DIR="$REPO_ROOT/docs/evidence/$(date +%Y%m%d-%H%M)"

# Configuration
DB_NAME="${ODOO_DB:-odoo_core}"
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
DOCKER_MODE="${DOCKER_MODE:-true}"
CONTAINER_NAME="${ODOO_CONTAINER:-odoo-core}"
SUPERSET_URL="${SUPERSET_URL:-http://localhost:8088}"

# Output mode
VERBOSE=false
JSON_OUTPUT=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_step() { echo -e "${BLUE}[CHECK]${NC} $1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Create evidence directory
mkdir -p "$EVIDENCE_DIR"

# Results tracking
declare -A RESULTS
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

record_result() {
    local check_name="$1"
    local status="$2"
    local details="${3:-}"

    RESULTS["$check_name"]="$status"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ "$status" == "pass" ]]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        log_pass "$check_name"
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        log_fail "$check_name${details:+ - $details}"
    fi
}

# === Health Checks ===

log_step "Odoo Web Health Check"
if ODOO_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$ODOO_URL/web/health" 2>/dev/null); then
    if [[ "$ODOO_HEALTH" == "200" ]]; then
        record_result "odoo_health" "pass"
    else
        record_result "odoo_health" "fail" "HTTP $ODOO_HEALTH"
    fi
else
    record_result "odoo_health" "fail" "Connection refused"
fi

log_step "PostgreSQL Connectivity"
if $DOCKER_MODE; then
    if docker compose exec -T postgres pg_isready -U odoo -d "$DB_NAME" >/dev/null 2>&1; then
        record_result "postgres_ready" "pass"
    else
        record_result "postgres_ready" "fail"
    fi
else
    if pg_isready -h localhost -p 5432 -U odoo >/dev/null 2>&1; then
        record_result "postgres_ready" "pass"
    else
        record_result "postgres_ready" "fail"
    fi
fi

log_step "Superset Health Check (if configured)"
if SUPERSET_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$SUPERSET_URL/health" 2>/dev/null); then
    if [[ "$SUPERSET_HEALTH" == "200" ]]; then
        record_result "superset_health" "pass"
    else
        record_result "superset_health" "skip" "HTTP $SUPERSET_HEALTH"
    fi
else
    record_result "superset_health" "skip" "Not running"
fi

# === Module Installation Checks ===

log_step "Verifying installed OCA modules"

# Core OCA modules to verify
CORE_MODULES=(
    "date_range"
    "base_tier_validation"
    "web_responsive"
    "report_xlsx"
    "mis_builder"
    "dms"
    "base_rest"
    "mail_activity_board"
    "contract"
)

check_module_installed() {
    local module="$1"
    local result

    if $DOCKER_MODE; then
        result=$(docker compose exec -T "$CONTAINER_NAME" odoo shell -d "$DB_NAME" --no-http -c "
from odoo import api, SUPERUSER_ID
import sys
cr = odoo.registry('$DB_NAME').cursor()
env = api.Environment(cr, SUPERUSER_ID, {})
mod = env['ir.module.module'].search([('name', '=', '$module'), ('state', '=', 'installed')])
print('installed' if mod else 'not_installed')
cr.close()
sys.exit(0)
" 2>/dev/null | tail -1) || result="error"
    else
        result="skip"  # Non-docker check would go here
    fi

    if [[ "$result" == "installed" ]]; then
        return 0
    else
        return 1
    fi
}

for module in "${CORE_MODULES[@]}"; do
    if check_module_installed "$module" 2>/dev/null; then
        record_result "module_$module" "pass"
    else
        record_result "module_$module" "fail" "Not installed or error"
    fi
done

# === Database Checks ===

log_step "Database structure verification"

if $DOCKER_MODE; then
    # Check key tables exist
    TABLE_CHECK=$(docker compose exec -T postgres psql -U odoo -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('res_users', 'ir_module_module', 'account_move', 'mis_report');
    " 2>/dev/null | tr -d ' ') || TABLE_CHECK="0"

    if [[ "$TABLE_CHECK" -ge 3 ]]; then
        record_result "db_tables" "pass"
    else
        record_result "db_tables" "fail" "Missing tables"
    fi
else
    record_result "db_tables" "skip"
fi

# === Container Checks ===

if $DOCKER_MODE; then
    log_step "Docker container status"

    # Check Odoo container
    ODOO_STATUS=$(docker compose ps --format json "$CONTAINER_NAME" 2>/dev/null | jq -r '.State' 2>/dev/null) || ODOO_STATUS="unknown"
    if [[ "$ODOO_STATUS" == "running" ]]; then
        record_result "container_odoo" "pass"
    else
        record_result "container_odoo" "fail" "State: $ODOO_STATUS"
    fi

    # Check PostgreSQL container
    PG_STATUS=$(docker compose ps --format json postgres 2>/dev/null | jq -r '.State' 2>/dev/null) || PG_STATUS="unknown"
    if [[ "$PG_STATUS" == "running" ]]; then
        record_result "container_postgres" "pass"
    else
        record_result "container_postgres" "fail" "State: $PG_STATUS"
    fi
fi

# === Performance Check ===

log_step "Basic performance check"

START_TIME=$(date +%s%N)
curl -s -o /dev/null "$ODOO_URL/web/login" 2>/dev/null || true
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to ms

if [[ $RESPONSE_TIME -lt 3000 ]]; then
    record_result "perf_login_page" "pass" "${RESPONSE_TIME}ms"
else
    record_result "perf_login_page" "warn" "${RESPONSE_TIME}ms (slow)"
fi

# === Generate Evidence ===

log_step "Generating evidence files"

# Git state
{
    echo "# Git State"
    echo "Branch: $(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo 'unknown')"
    echo "HEAD: $(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown')"
    echo ""
    echo "## Diff stats"
    git -C "$REPO_ROOT" diff --stat 2>/dev/null || echo "No changes"
} > "$EVIDENCE_DIR/git_state.md"

# Verification results
{
    echo "# Stack Verification Results"
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "## Summary"
    echo "- Total checks: $TOTAL_CHECKS"
    echo "- Passed: $PASSED_CHECKS"
    echo "- Failed: $FAILED_CHECKS"
    echo ""
    echo "## Details"
    for check in "${!RESULTS[@]}"; do
        echo "- $check: ${RESULTS[$check]}"
    done
} > "$EVIDENCE_DIR/verification_results.md"

# Container logs (if Docker)
if $DOCKER_MODE; then
    docker compose logs --tail=100 "$CONTAINER_NAME" > "$EVIDENCE_DIR/odoo_logs.txt" 2>/dev/null || true
    docker compose logs --tail=50 postgres > "$EVIDENCE_DIR/postgres_logs.txt" 2>/dev/null || true
fi

# === JSON Output ===

if $JSON_OUTPUT; then
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
        echo "  \"total_checks\": $TOTAL_CHECKS,"
        echo "  \"passed\": $PASSED_CHECKS,"
        echo "  \"failed\": $FAILED_CHECKS,"
        echo "  \"results\": {"
        FIRST=true
        for check in "${!RESULTS[@]}"; do
            if ! $FIRST; then echo ","; fi
            FIRST=false
            echo -n "    \"$check\": \"${RESULTS[$check]}\""
        done
        echo ""
        echo "  }"
        echo "}"
    } > "$EVIDENCE_DIR/results.json"
fi

# === Final Summary ===

echo ""
echo "===== Verification Summary ====="
echo "Total checks:  $TOTAL_CHECKS"
echo "Passed:        $PASSED_CHECKS"
echo "Failed:        $FAILED_CHECKS"
echo ""
echo "Evidence written to: $EVIDENCE_DIR/"

if [[ $FAILED_CHECKS -eq 0 ]]; then
    log_pass "All checks passed!"
    exit 0
else
    log_warn "Some checks failed - review evidence for details"
    exit 1
fi
