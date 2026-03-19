#!/usr/bin/env bash
# =============================================================================
# VERIFY WORKOS DEPLOYMENT
# =============================================================================
# Quick verification script for WorkOS module deployment.
# Run after deploy_workos.sh to confirm everything is working.
#
# Usage:
#   ./scripts/prod/verify_workos.sh
# =============================================================================

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/opt/odoo-ce}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE:-deploy/docker-compose.workos-deploy.yml}"
DB_SERVICE="${DB_SERVICE:-db}"
DB_NAME="${DB_NAME:-odoo}"
DB_USER="${DB_USER:-odoo}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
BASE_URL="${BASE_URL:-https://erp.insightpulseai.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

cd "$REPO_ROOT"

echo "=============================================="
echo "  WORKOS DEPLOYMENT VERIFICATION"
echo "=============================================="
echo ""

errors=0

# -----------------------------------------------------------------------------
# 1. HTTP Checks
# -----------------------------------------------------------------------------
echo "=== HTTP Checks ==="

# Internal check (via container)
http_internal=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$ODOO_SERVICE" curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login 2>/dev/null || echo "000")

if [[ "$http_internal" == "200" ]] || [[ "$http_internal" == "303" ]]; then
    pass "Internal HTTP: $http_internal"
else
    fail "Internal HTTP: $http_internal"
    errors=$((errors + 1))
fi

# External check
http_external=$(curl -s -o /dev/null -w "%{http_code}" -I "$BASE_URL/web/login" 2>/dev/null || echo "000")

if [[ "$http_external" == "200" ]] || [[ "$http_external" == "303" ]]; then
    pass "External HTTP ($BASE_URL): $http_external"
else
    warn "External HTTP ($BASE_URL): $http_external"
fi

echo ""

# -----------------------------------------------------------------------------
# 2. Module State Checks
# -----------------------------------------------------------------------------
echo "=== Module State Checks ==="

# Check umbrella module
umbrella_state=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
    "SELECT state FROM ir_module_module WHERE name = 'ipai_workos_affine';" 2>/dev/null || echo "unknown")

if [[ "$umbrella_state" == "installed" ]]; then
    pass "ipai_workos_affine: installed"
else
    fail "ipai_workos_affine: $umbrella_state"
    errors=$((errors + 1))
fi

# Check all WorkOS modules
workos_installed=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM ir_module_module WHERE name LIKE 'ipai_workos_%' AND state = 'installed';" 2>/dev/null || echo "0")

if [[ "$workos_installed" -ge 9 ]]; then
    pass "WorkOS modules installed: $workos_installed"
else
    fail "WorkOS modules installed: $workos_installed (expected >= 9)"
    errors=$((errors + 1))
fi

# Check platform modules
platform_installed=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM ir_module_module WHERE name LIKE 'ipai_platform_%' AND state = 'installed';" 2>/dev/null || echo "0")

if [[ "$platform_installed" -ge 2 ]]; then
    pass "Platform modules installed: $platform_installed"
else
    warn "Platform modules installed: $platform_installed (expected >= 2)"
fi

echo ""

# -----------------------------------------------------------------------------
# 3. Model Checks
# -----------------------------------------------------------------------------
echo "=== Model Checks ==="

workos_models=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM ir_model WHERE model LIKE 'ipai.workos.%';" 2>/dev/null || echo "0")

if [[ "$workos_models" -ge 5 ]]; then
    pass "WorkOS models registered: $workos_models"
else
    warn "WorkOS models registered: $workos_models (expected >= 5)"
fi

echo ""

# -----------------------------------------------------------------------------
# 4. Log Checks
# -----------------------------------------------------------------------------
echo "=== Log Checks ==="

traceback_count=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    logs --tail=200 "$ODOO_SERVICE" 2>&1 | grep -ic "traceback" || echo "0")

if [[ "$traceback_count" -eq 0 ]]; then
    pass "No tracebacks in recent logs"
else
    warn "Tracebacks in recent logs: $traceback_count"
fi

error_count=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    logs --tail=200 "$ODOO_SERVICE" 2>&1 | grep -icE "^.*ERROR" || echo "0")

if [[ "$error_count" -le 2 ]]; then
    pass "Errors in recent logs: $error_count"
else
    warn "Errors in recent logs: $error_count"
fi

echo ""

# -----------------------------------------------------------------------------
# 5. Container Checks
# -----------------------------------------------------------------------------
echo "=== Container Checks ==="

# Check addons visibility
addons_visible=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
    exec -T "$ODOO_SERVICE" ls /mnt/addons/ipai/ipai_workos_affine 2>/dev/null && echo "yes" || echo "no")

if [[ "$addons_visible" == "yes" ]]; then
    pass "Addons visible in container"
else
    fail "Addons NOT visible in container"
    errors=$((errors + 1))
fi

echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "=============================================="
if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}VERIFICATION PASSED${NC}"
    echo "All critical checks passed."
else
    echo -e "${RED}VERIFICATION FAILED${NC}"
    echo "$errors critical check(s) failed."
    echo ""
    echo "Troubleshooting:"
    echo "  - Check logs: docker compose -f $COMPOSE_FILE logs odoo"
    echo "  - Check modules: psql -c \"SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_%'\""
    echo "  - Rollback: ./scripts/prod/deploy_workos.sh --rollback"
fi
echo "=============================================="

exit $errors
