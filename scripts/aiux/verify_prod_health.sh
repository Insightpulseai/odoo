#!/bin/bash
set -euo pipefail

# Production Health Verification Script
# Prevents deployment loops by validating runtime health contracts

COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.v0.10.0.yml}"
BASE_URL="${BASE_URL:-https://erp.insightpulseai.net}"
DB_NAME="${DB_NAME:-odoo_core}"

echo "=== Odoo Production Health Verification ==="
echo "Compose file: $COMPOSE_FILE"
echo "Base URL: $BASE_URL"
echo "Database: $DB_NAME"
echo ""

# Color codes
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Container Health Check
echo "=== 1. Container Health ==="
if docker compose -f "$COMPOSE_FILE" ps | grep -q "odoo.*healthy"; then
    check_pass "Odoo container is healthy"
else
    check_fail "Odoo container is not healthy"
fi

if docker compose -f "$COMPOSE_FILE" ps | grep -q "db.*healthy\|postgres.*healthy"; then
    check_pass "Database container is healthy"
else
    check_fail "Database container is not healthy"
fi

# 2. Database Connection Check
echo ""
echo "=== 2. Database Connection ==="
if docker exec odoo-postgres psql -U odoo -d "$DB_NAME" -c "SELECT 1;" &>/dev/null; then
    check_pass "Database connection successful"
else
    check_fail "Database connection failed"
fi

# 3. HTTP Endpoint Checks
echo ""
echo "=== 3. HTTP Endpoints ==="

# Login page
LOGIN_CODE=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/web/login" || echo "000")
if [[ "$LOGIN_CODE" == "200" ]]; then
    check_pass "Login page returns 200"
else
    check_fail "Login page returns $LOGIN_CODE (expected 200)"
fi

# Web app
WEB_CODE=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/web" || echo "000")
if [[ "$WEB_CODE" == "200" || "$WEB_CODE" == "303" ]]; then
    check_pass "Web app returns $WEB_CODE (valid)"
else
    check_fail "Web app returns $WEB_CODE (expected 200/303)"
fi

# Frontend CSS
CSS_CODE=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/web/assets/1/0/web.assets_frontend.min.css" || echo "000")
if [[ "$CSS_CODE" == "200" || "$CSS_CODE" == "303" ]]; then
    check_pass "CSS assets return $CSS_CODE (valid)"
else
    check_fail "CSS assets return $CSS_CODE (expected 200/303)"
fi

# Frontend JS
JS_CODE=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/web/assets/1/0/web.assets_frontend_minimal.min.js" || echo "000")
if [[ "$JS_CODE" == "200" || "$JS_CODE" == "303" ]]; then
    check_pass "JS assets return $JS_CODE (valid)"
else
    check_fail "JS assets return $JS_CODE (expected 200/303)"
fi

# 4. Log Health Check
echo ""
echo "=== 4. Log Health (no critical errors) ==="

# Check for database connection errors
if docker exec odoo-ce tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -qi "psycopg2.OperationalError"; then
    check_fail "Found database connection errors in logs"
else
    check_pass "No database connection errors"
fi

# Check for OWL errors
if docker exec odoo-ce tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -qi "OwlError"; then
    check_warn "Found OWL errors in logs (may be client-side)"
else
    check_pass "No OWL errors in server logs"
fi

# Check for asset errors
if docker exec odoo-ce tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -qi "KeyError.*assets"; then
    check_fail "Found asset KeyErrors in logs"
else
    check_pass "No asset KeyErrors"
fi

# Check for critical errors
CRITICAL_COUNT=$(docker exec odoo-ce tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -c "CRITICAL" || echo "0")
if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
    check_fail "Found $CRITICAL_COUNT CRITICAL errors in logs"
else
    check_pass "No CRITICAL errors"
fi

# 5. Config Invariants Check
echo ""
echo "=== 5. Config Invariants ==="

CONFIG_FILE="${CONFIG_FILE:-deploy/odoo.conf}"
if [[ -f "$CONFIG_FILE" ]]; then
    # Check db_host
    if grep -q "^db_host = postgres$" "$CONFIG_FILE"; then
        check_pass "db_host = postgres (correct)"
    else
        check_fail "db_host is not 'postgres'"
    fi

    # Check db_name
    if grep -q "^db_name = False$" "$CONFIG_FILE"; then
        check_pass "db_name = False (correct)"
    else
        check_warn "db_name is not False (may be intentional)"
    fi

    # Check dbfilter exists
    if grep -q "^dbfilter" "$CONFIG_FILE"; then
        check_pass "dbfilter is configured"
    else
        check_warn "dbfilter is not configured"
    fi

    # Check list_db
    if grep -q "^list_db = False$" "$CONFIG_FILE"; then
        check_pass "list_db = False (secure)"
    else
        check_warn "list_db is not False"
    fi

    # Check log_level
    if grep -q "^log_level = info$" "$CONFIG_FILE"; then
        check_pass "log_level = info (production)"
    elif grep -q "^log_level = debug$" "$CONFIG_FILE"; then
        check_warn "log_level = debug (should be info in production)"
    fi
else
    check_fail "Config file not found: $CONFIG_FILE"
fi

# 6. Module Health Check
echo ""
echo "=== 6. Module Health ==="

# Check for modules stuck in 'to upgrade' state
UPGRADE_COUNT=$(docker exec odoo-postgres psql -U odoo -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM ir_module_module WHERE state='to upgrade';" 2>/dev/null | tr -d ' \n' || echo "0")
UPGRADE_COUNT=${UPGRADE_COUNT:-0}
if [[ "$UPGRADE_COUNT" -gt 0 ]]; then
    check_warn "$UPGRADE_COUNT modules in 'to upgrade' state (may be expected)"
else
    check_pass "No modules pending upgrade"
fi

# Check for modules in 'to install' state
INSTALL_COUNT=$(docker exec odoo-postgres psql -U odoo -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM ir_module_module WHERE state='to install';" 2>/dev/null | tr -d ' \n' || echo "0")
INSTALL_COUNT=${INSTALL_COUNT:-0}
if [[ "$INSTALL_COUNT" -gt 0 ]]; then
    check_warn "$INSTALL_COUNT modules in 'to install' state"
else
    check_pass "No modules pending installation"
fi

# Summary
echo ""
echo "=== Health Check Summary ==="
if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}$FAILED health checks failed${NC}"
    exit 1
fi
