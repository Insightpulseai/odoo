#!/usr/bin/env bash
# =============================================================================
# Odoo CE Smoke Test Suite
# =============================================================================
# Comprehensive smoke tests for Odoo CE deployment validation.
# Tests web accessibility, database connectivity, and core functionality.
#
# Usage:
#   ./scripts/smoke_test_odoo.sh [--url URL] [--db DATABASE] [--verbose]
#
# Options:
#   --url URL       Odoo base URL (default: http://localhost:8069)
#   --db DATABASE   Database name (default: odoo_core)
#   --verbose       Show detailed output
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
DATABASE="${ODOO_DB:-odoo_core}"
VERBOSE=false
PASSED=0
FAILED=0
WARNINGS=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            ODOO_URL="$2"
            shift 2
            ;;
        --db)
            DATABASE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Test result functions
pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

skip() {
    echo -e "  ${BLUE}○${NC} $1 (skipped)"
}

# Banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Odoo CE Smoke Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Target URL: ${BLUE}$ODOO_URL${NC}"
echo -e "  Database:   ${BLUE}$DATABASE${NC}"
echo ""

# =============================================================================
# Test Group 1: Network Connectivity
# =============================================================================
echo -e "${BLUE}━━━ Network Connectivity ━━━${NC}"

# Test 1.1: Base URL accessible
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|301|302|303|307|308)$ ]]; then
    pass "Base URL accessible (HTTP $HTTP_CODE)"
elif [[ "$HTTP_CODE" == "000" ]]; then
    fail "Base URL not reachable (connection failed)"
else
    warn "Base URL returned HTTP $HTTP_CODE"
fi

# Test 1.2: Health endpoint
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/web/health" 2>/dev/null || echo "000")
if [[ "$HEALTH_CODE" == "200" ]]; then
    pass "Health endpoint responding (HTTP 200)"
elif [[ "$HEALTH_CODE" == "404" ]]; then
    # Health endpoint might not exist in older versions
    warn "Health endpoint not found (HTTP 404)"
else
    warn "Health endpoint returned HTTP $HEALTH_CODE"
fi

# Test 1.3: Login page accessible
LOGIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/web/login" 2>/dev/null || echo "000")
if [[ "$LOGIN_CODE" =~ ^(200|303)$ ]]; then
    pass "Login page accessible (HTTP $LOGIN_CODE)"
else
    fail "Login page not accessible (HTTP $LOGIN_CODE)"
fi

echo ""

# =============================================================================
# Test Group 2: Web Interface
# =============================================================================
echo -e "${BLUE}━━━ Web Interface ━━━${NC}"

# Test 2.1: Login page contains expected elements
LOGIN_CONTENT=$(curl -s --connect-timeout 10 "$ODOO_URL/web/login" 2>/dev/null || echo "")
if echo "$LOGIN_CONTENT" | grep -qi "odoo"; then
    pass "Login page contains Odoo branding"
else
    warn "Login page may not contain expected content"
fi

# Test 2.2: Static assets loading
CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/web/static/lib/jquery/jquery.js" 2>/dev/null || echo "000")
if [[ "$CSS_CODE" == "200" ]]; then
    pass "Static assets accessible"
elif [[ "$CSS_CODE" == "404" ]]; then
    # Different path in different versions
    ALT_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/web/static/src/libs/jquery.js" 2>/dev/null || echo "000")
    if [[ "$ALT_CODE" == "200" ]]; then
        pass "Static assets accessible (alt path)"
    else
        warn "Static assets path may differ"
    fi
else
    warn "Static assets returned HTTP $CSS_CODE"
fi

# Test 2.3: Database selector available
DB_SELECTOR=$(curl -s --connect-timeout 10 "$ODOO_URL/web/database/selector" 2>/dev/null || echo "")
if echo "$DB_SELECTOR" | grep -qi "database\|odoo"; then
    pass "Database selector accessible"
else
    skip "Database selector (may require auth)"
fi

echo ""

# =============================================================================
# Test Group 3: Database Connectivity
# =============================================================================
echo -e "${BLUE}━━━ Database Connectivity ━━━${NC}"

# Test 3.1: Check if database exists via Odoo API
DB_LIST=$(curl -s --connect-timeout 10 -X POST "$ODOO_URL/web/database/list" -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "")
if echo "$DB_LIST" | grep -q "$DATABASE"; then
    pass "Database '$DATABASE' exists"
elif echo "$DB_LIST" | grep -qi "error\|unauthorized"; then
    skip "Database list (access restricted)"
else
    warn "Database '$DATABASE' not found in list"
fi

# Test 3.2: Direct PostgreSQL check (if Docker)
if command -v docker &>/dev/null; then
    COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
    if [[ -f "$COMPOSE_FILE" ]]; then
        PG_CHECK=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -d "$DATABASE" -c "SELECT 1;" 2>/dev/null || echo "")
        if echo "$PG_CHECK" | grep -q "1"; then
            pass "Direct PostgreSQL connection verified"
        else
            skip "Direct PostgreSQL check (container may not be running)"
        fi
    else
        skip "Direct PostgreSQL check (no docker-compose.yml)"
    fi
else
    skip "Direct PostgreSQL check (Docker not available)"
fi

echo ""

# =============================================================================
# Test Group 4: API Endpoints
# =============================================================================
echo -e "${BLUE}━━━ API Endpoints ━━━${NC}"

# Test 4.1: JSON-RPC endpoint
RPC_RESPONSE=$(curl -s -X POST "$ODOO_URL/jsonrpc" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"call","params":{"service":"common","method":"version","args":[]},"id":1}' \
    --connect-timeout 10 2>/dev/null || echo "")

if echo "$RPC_RESPONSE" | grep -q "server_version"; then
    VERSION=$(echo "$RPC_RESPONSE" | grep -o '"server_version"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"server_version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    pass "JSON-RPC endpoint responding (Odoo $VERSION)"
elif echo "$RPC_RESPONSE" | grep -qi "error"; then
    warn "JSON-RPC endpoint returned error"
else
    fail "JSON-RPC endpoint not responding"
fi

# Test 4.2: XML-RPC common endpoint
XMLRPC_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/xmlrpc/2/common" 2>/dev/null || echo "000")
if [[ "$XMLRPC_CODE" == "200" ]]; then
    pass "XML-RPC common endpoint accessible"
elif [[ "$XMLRPC_CODE" == "405" ]]; then
    # Method not allowed is expected for GET on XML-RPC
    pass "XML-RPC common endpoint accessible (POST required)"
else
    warn "XML-RPC common endpoint returned HTTP $XMLRPC_CODE"
fi

# Test 4.3: Web manifest
MANIFEST_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$ODOO_URL/web/manifest.webmanifest" 2>/dev/null || echo "000")
if [[ "$MANIFEST_CODE" == "200" ]]; then
    pass "Web manifest accessible"
else
    skip "Web manifest (may not exist in this version)"
fi

echo ""

# =============================================================================
# Test Group 5: Module Status (if accessible)
# =============================================================================
echo -e "${BLUE}━━━ Module Status ━━━${NC}"

# Test 5.1: Check for IPAI modules via shell (if Docker available)
if command -v docker &>/dev/null; then
    COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
    if [[ -f "$COMPOSE_FILE" ]]; then
        IPAI_COUNT=$(docker compose -f "$COMPOSE_FILE" exec -T odoo-core ls /mnt/extra-addons/ipai/ 2>/dev/null | wc -l || echo "0")
        if [[ "$IPAI_COUNT" -gt 0 ]]; then
            pass "IPAI modules directory accessible ($IPAI_COUNT items)"
        else
            warn "IPAI modules directory empty or not accessible"
        fi
    else
        skip "Module check (no docker-compose.yml)"
    fi
else
    skip "Module check (Docker not available)"
fi

# Test 5.2: Check OCA modules directory
if command -v docker &>/dev/null; then
    COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
    if [[ -f "$COMPOSE_FILE" ]]; then
        OCA_CHECK=$(docker compose -f "$COMPOSE_FILE" exec -T odoo-core test -d /mnt/extra-addons/oca 2>/dev/null && echo "exists" || echo "missing")
        if [[ "$OCA_CHECK" == "exists" ]]; then
            pass "OCA modules directory exists"
        else
            warn "OCA modules directory not found"
        fi
    fi
fi

echo ""

# =============================================================================
# Test Group 6: Performance Baseline
# =============================================================================
echo -e "${BLUE}━━━ Performance Baseline ━━━${NC}"

# Test 6.1: Response time check
START_TIME=$(date +%s%N)
curl -s -o /dev/null --connect-timeout 10 "$ODOO_URL/web/login" 2>/dev/null
END_TIME=$(date +%s%N)
RESPONSE_MS=$(( (END_TIME - START_TIME) / 1000000 ))

if [[ $RESPONSE_MS -lt 1000 ]]; then
    pass "Response time acceptable (${RESPONSE_MS}ms)"
elif [[ $RESPONSE_MS -lt 3000 ]]; then
    warn "Response time slow (${RESPONSE_MS}ms)"
else
    fail "Response time too slow (${RESPONSE_MS}ms)"
fi

# Test 6.2: Memory check (if Docker)
if command -v docker &>/dev/null; then
    COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
    if [[ -f "$COMPOSE_FILE" ]]; then
        MEM_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" $(docker compose -f "$COMPOSE_FILE" ps -q odoo-core 2>/dev/null) 2>/dev/null | head -1 || echo "N/A")
        if [[ "$MEM_USAGE" != "N/A" ]] && [[ -n "$MEM_USAGE" ]]; then
            pass "Memory usage: $MEM_USAGE"
        else
            skip "Memory check (container stats not available)"
        fi
    fi
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Smoke Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}   $PASSED"
echo -e "  ${RED}Failed:${NC}   $FAILED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}$FAILED critical test(s) failed${NC}"
    exit 1
fi
