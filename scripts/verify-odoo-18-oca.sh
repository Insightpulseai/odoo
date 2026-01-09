#!/bin/bash
# =============================================================================
# Odoo 18 CE + OCA Verification Script
# =============================================================================
# STEP 6: Verify installation with evidence
#
# Checks:
#   1. HTTP check: curl /web returns 200 (or login HTML)
#   2. Module state proof (SQL): list installed modules
#   3. Odoo server log excerpt showing successful boot
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
DB_NAME="${ODOO_DB_NAME:-odoo_core}"

echo ""
echo "============================================================================="
echo "               ODOO 18 CE + OCA VERIFICATION"
echo "============================================================================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((CHECKS_PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((CHECKS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

# =============================================================================
# CHECK 1: External code present
# =============================================================================
echo "--- CHECK 1: OCA External Code Present ---"

if ls -la "${PROJECT_ROOT}/addons/OCA" 2>/dev/null | grep -q "server-tools"; then
    pass "OCA/server-tools directory exists"
else
    fail "OCA/server-tools directory missing"
fi

if ls -la "${PROJECT_ROOT}/addons/OCA" 2>/dev/null | grep -q "sale-workflow"; then
    pass "OCA/sale-workflow directory exists"
else
    fail "OCA/sale-workflow directory missing"
fi

if ls -la "${PROJECT_ROOT}/addons/OCA" 2>/dev/null | grep -q "automation"; then
    pass "OCA/automation directory exists"
else
    fail "OCA/automation directory missing"
fi

# =============================================================================
# CHECK 2: addons_path generated
# =============================================================================
echo ""
echo "--- CHECK 2: addons_path Generation ---"

if [ -f "${PROJECT_ROOT}/scripts/gen_addons_path.py" ]; then
    ADDONS_PATH=$(python3 "${PROJECT_ROOT}/scripts/gen_addons_path.py" 2>/dev/null || echo "")
    if [ -n "$ADDONS_PATH" ]; then
        PATH_COUNT=$(echo "$ADDONS_PATH" | tr ',' '\n' | wc -l)
        pass "addons_path generated with $PATH_COUNT paths"
        info "First 5 paths:"
        echo "$ADDONS_PATH" | tr ',' '\n' | head -5 | sed 's/^/    /'
    else
        fail "addons_path generation failed"
    fi
else
    fail "gen_addons_path.py script not found"
fi

# =============================================================================
# CHECK 3: OCA modules manifest files
# =============================================================================
echo ""
echo "--- CHECK 3: OCA Module Manifests ---"

MANIFEST_COUNT=$(find "${PROJECT_ROOT}/addons/OCA" -maxdepth 3 -name "__manifest__.py" 2>/dev/null | wc -l)
if [ "$MANIFEST_COUNT" -gt 0 ]; then
    pass "Found $MANIFEST_COUNT OCA module manifests"
    info "Sample modules:"
    find "${PROJECT_ROOT}/addons/OCA" -maxdepth 3 -name "__manifest__.py" 2>/dev/null | head -5 | \
        sed 's|.*/OCA/||; s|/__manifest__.py||' | sed 's/^/    /'
else
    fail "No OCA module manifests found"
fi

# =============================================================================
# CHECK 4: HTTP check (if Docker available)
# =============================================================================
echo ""
echo "--- CHECK 4: HTTP Health Check ---"

if command -v docker &> /dev/null; then
    if docker compose ps odoo-core 2>/dev/null | grep -q "running"; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${ODOO_URL}/web" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "303" ]; then
            pass "HTTP check: ${ODOO_URL}/web returned $HTTP_CODE"
        else
            fail "HTTP check: ${ODOO_URL}/web returned $HTTP_CODE (expected 200/303)"
        fi
    else
        warn "odoo-core container not running - skipping HTTP check"
    fi
else
    warn "Docker not available - skipping HTTP check"
fi

# =============================================================================
# CHECK 5: Module state proof (SQL)
# =============================================================================
echo ""
echo "--- CHECK 5: Module State (Database) ---"

if command -v docker &> /dev/null; then
    if docker compose ps postgres 2>/dev/null | grep -q "running"; then
        info "Checking installed modules in database..."

        # Core CE modules
        CORE_MODULES="account,sale_management,mass_mailing,crm"
        for mod in $(echo $CORE_MODULES | tr ',' ' '); do
            STATE=$(docker compose exec -T postgres psql -U odoo -d "$DB_NAME" -t -c \
                "SELECT state FROM ir_module_module WHERE name='$mod'" 2>/dev/null | tr -d ' \n' || echo "unknown")
            if [ "$STATE" = "installed" ]; then
                pass "Module '$mod' state: installed"
            else
                warn "Module '$mod' state: ${STATE:-not found}"
            fi
        done

        # OCA modules (sample)
        info "Checking OCA module states..."
        OCA_MODULES="date_range,web_responsive,account_fiscal_year"
        for mod in $(echo $OCA_MODULES | tr ',' ' '); do
            STATE=$(docker compose exec -T postgres psql -U odoo -d "$DB_NAME" -t -c \
                "SELECT state FROM ir_module_module WHERE name='$mod'" 2>/dev/null | tr -d ' \n' || echo "unknown")
            if [ "$STATE" = "installed" ]; then
                pass "OCA module '$mod' state: installed"
            elif [ "$STATE" = "uninstalled" ]; then
                warn "OCA module '$mod' state: uninstalled (available but not installed)"
            else
                warn "OCA module '$mod' state: ${STATE:-not in database}"
            fi
        done
    else
        warn "postgres container not running - skipping database check"
    fi
else
    warn "Docker not available - skipping database check"
fi

# =============================================================================
# CHECK 6: Server log excerpt
# =============================================================================
echo ""
echo "--- CHECK 6: Server Log ---"

if command -v docker &> /dev/null; then
    if docker compose ps odoo-core 2>/dev/null | grep -q "running"; then
        info "Last 10 log lines from odoo-core:"
        docker compose logs --tail=10 odoo-core 2>/dev/null | sed 's/^/    /' || warn "Could not read logs"
    else
        warn "odoo-core container not running - skipping log check"
    fi
else
    warn "Docker not available - skipping log check"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "============================================================================="
echo "                     VERIFICATION SUMMARY"
echo "============================================================================="
echo ""
echo -e "Passed: ${GREEN}${CHECKS_PASSED}${NC}"
echo -e "Failed: ${RED}${CHECKS_FAILED}${NC}"
echo ""

if [ "$CHECKS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some checks failed. Review above for details.${NC}"
    exit 1
fi
