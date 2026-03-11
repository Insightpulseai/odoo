#!/bin/bash
# =============================================================================
# AIUX Ship Bundle v1.1.0 - Installation Verification Script
# =============================================================================
# Usage: ./scripts/aiux/verify_install.sh [COMPOSE_FILE] [DB_NAME]
#
# This script verifies that all ship modules are properly installed and
# the Odoo instance is healthy.
# =============================================================================

set -euo pipefail

# Configuration
COMPOSE_FILE="${1:-docker-compose.prod.yml}"
DB_NAME="${2:-odoo}"
SHIP_VERSION="1.1.0"
SHIP_MODULES=(
    "ipai_theme_aiux"
    "ipai_aiux_chat"
    "ipai_ask_ai"
    "ipai_document_ai"
    "ipai_expense_ocr"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Output helpers
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=============================================="
echo "AIUX Ship Bundle v${SHIP_VERSION} - Install Verification"
echo "=============================================="
echo ""

# Track failures
FAILURES=0

# -----------------------------------------------------------------------------
# Check 1: Docker compose file exists
# -----------------------------------------------------------------------------
info "Checking compose file..."
if [ ! -f "$COMPOSE_FILE" ]; then
    error "Compose file not found: $COMPOSE_FILE"
    FAILURES=$((FAILURES + 1))
else
    echo "  ✅ Compose file exists: $COMPOSE_FILE"
fi

# -----------------------------------------------------------------------------
# Check 2: Containers are running
# -----------------------------------------------------------------------------
info "Checking container status..."
if ! docker compose -f "$COMPOSE_FILE" ps --format json 2>/dev/null | grep -q '"State":"running"'; then
    warn "Containers may not be running. Checking status..."
    docker compose -f "$COMPOSE_FILE" ps
fi

# Check Odoo container specifically
ODOO_STATUS=$(docker compose -f "$COMPOSE_FILE" ps odoo --format '{{.Status}}' 2>/dev/null || echo "not found")
if [[ "$ODOO_STATUS" == *"Up"* ]]; then
    echo "  ✅ Odoo container is running"
else
    error "Odoo container is not running: $ODOO_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# Check DB container
DB_STATUS=$(docker compose -f "$COMPOSE_FILE" ps db --format '{{.Status}}' 2>/dev/null || echo "not found")
if [[ "$DB_STATUS" == *"Up"* ]]; then
    echo "  ✅ Database container is running"
else
    error "Database container is not running: $DB_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 3: Module files exist in container
# -----------------------------------------------------------------------------
info "Checking module files in container..."
for module in "${SHIP_MODULES[@]}"; do
    if docker compose -f "$COMPOSE_FILE" exec -T odoo test -f "/mnt/addons/ipai/${module}/__manifest__.py" 2>/dev/null; then
        echo "  ✅ ${module} files present"
    else
        # Try alternative path
        if docker compose -f "$COMPOSE_FILE" exec -T odoo test -f "/mnt/extra-addons/ipai/${module}/__manifest__.py" 2>/dev/null; then
            echo "  ✅ ${module} files present (extra-addons)"
        else
            error "${module} files not found in container"
            FAILURES=$((FAILURES + 1))
        fi
    fi
done

# -----------------------------------------------------------------------------
# Check 4: Modules installed in database
# -----------------------------------------------------------------------------
info "Checking module installation in database..."
for module in "${SHIP_MODULES[@]}"; do
    INSTALLED=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
        odoo shell -d "$DB_NAME" --no-http <<EOF 2>/dev/null || echo "error"
try:
    mod = env['ir.module.module'].search([('name', '=', '${module}')])
    if mod and mod.state == 'installed':
        print('installed')
    elif mod:
        print(mod.state)
    else:
        print('not_found')
except Exception as e:
    print('error')
EOF
    )

    INSTALLED=$(echo "$INSTALLED" | tail -1 | tr -d '[:space:]')

    if [ "$INSTALLED" == "installed" ]; then
        echo "  ✅ ${module} installed"
    elif [ "$INSTALLED" == "uninstalled" ]; then
        warn "${module} exists but not installed"
    elif [ "$INSTALLED" == "not_found" ]; then
        error "${module} not found in module registry"
        FAILURES=$((FAILURES + 1))
    else
        warn "${module} status: ${INSTALLED}"
    fi
done

# -----------------------------------------------------------------------------
# Check 5: Health endpoint
# -----------------------------------------------------------------------------
info "Checking health endpoint..."
HEALTH_STATUS=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/health 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" == "200" ]; then
    echo "  ✅ /web/health returns 200"
else
    error "/web/health returns $HEALTH_STATUS (expected 200)"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 6: Login page
# -----------------------------------------------------------------------------
info "Checking login page..."
LOGIN_STATUS=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/login 2>/dev/null || echo "000")

if [ "$LOGIN_STATUS" == "200" ] || [ "$LOGIN_STATUS" == "303" ]; then
    echo "  ✅ /web/login returns $LOGIN_STATUS"
else
    error "/web/login returns $LOGIN_STATUS (expected 200 or 303)"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 7: Database connectivity
# -----------------------------------------------------------------------------
info "Checking database connectivity..."
DB_CHECK=$(docker compose -f "$COMPOSE_FILE" exec -T db \
    pg_isready -U odoo -d "$DB_NAME" 2>/dev/null || echo "failed")

if [[ "$DB_CHECK" == *"accepting connections"* ]]; then
    echo "  ✅ Database accepting connections"
else
    error "Database not accepting connections"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "Verification Summary"
echo "=============================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Ship Bundle v${SHIP_VERSION} is properly installed."
    exit 0
else
    echo -e "${RED}❌ ${FAILURES} check(s) failed${NC}"
    echo ""
    echo "Please review the errors above and fix before shipping."
    exit 1
fi
