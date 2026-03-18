#!/bin/bash
# =============================================================================
# AIUX Ship Bundle v1.1.0 - Assets Verification Script
# =============================================================================
# Usage: ./scripts/aiux/verify_assets.sh [COMPOSE_FILE] [BASE_URL]
#
# This script verifies that Odoo assets are properly compiled and accessible.
# Critical for preventing 500 errors on web client load.
# =============================================================================

set -euo pipefail

# Configuration
COMPOSE_FILE="${1:-docker-compose.prod.yml}"
BASE_URL="${2:-http://localhost:8069}"
SHIP_VERSION="1.1.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Output helpers
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=============================================="
echo "AIUX Ship Bundle v${SHIP_VERSION} - Assets Verification"
echo "=============================================="
echo ""

FAILURES=0

# -----------------------------------------------------------------------------
# Check 1: Backend assets bundle
# -----------------------------------------------------------------------------
info "Checking backend assets..."

# Try debug mode assets first (more verbose errors)
BACKEND_DEBUG=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' \
    "${BASE_URL}/web/assets/debug/web.assets_backend.js" 2>/dev/null || echo "000")

if [ "$BACKEND_DEBUG" == "200" ]; then
    echo "  ✅ web.assets_backend.js (debug) returns 200"
else
    warn "Debug assets returned $BACKEND_DEBUG, trying production..."

    BACKEND_PROD=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
        curl -sS -o /dev/null -w '%{http_code}' -L \
        "${BASE_URL}/web/assets/web.assets_backend.min.js" 2>/dev/null || echo "000")

    if [ "$BACKEND_PROD" == "200" ]; then
        echo "  ✅ web.assets_backend (minified) returns 200"
    else
        error "Backend JS assets not accessible (debug: $BACKEND_DEBUG, prod: $BACKEND_PROD)"
        FAILURES=$((FAILURES + 1))
    fi
fi

# -----------------------------------------------------------------------------
# Check 2: CSS assets
# -----------------------------------------------------------------------------
info "Checking CSS assets..."

CSS_STATUS=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' \
    "${BASE_URL}/web/assets/debug/web.assets_backend.css" 2>/dev/null || echo "000")

if [ "$CSS_STATUS" == "200" ]; then
    echo "  ✅ web.assets_backend.css returns 200"
else
    warn "CSS assets returned $CSS_STATUS"
    # Not a hard failure - CSS might be bundled differently
fi

# -----------------------------------------------------------------------------
# Check 3: QWeb templates
# -----------------------------------------------------------------------------
info "Checking QWeb templates..."

QWEB_STATUS=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' \
    "${BASE_URL}/web/webclient/qweb" 2>/dev/null || echo "000")

if [ "$QWEB_STATUS" == "200" ]; then
    echo "  ✅ QWeb templates endpoint returns 200"
else
    error "QWeb templates not accessible: $QWEB_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 4: Web client bootstrap
# -----------------------------------------------------------------------------
info "Checking web client bootstrap..."

# Load the login page and check for critical JS
LOGIN_CONTENT=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS "${BASE_URL}/web/login" 2>/dev/null || echo "")

if echo "$LOGIN_CONTENT" | grep -q "assets_backend"; then
    echo "  ✅ Login page references backend assets"
else
    warn "Login page may not reference backend assets correctly"
fi

if echo "$LOGIN_CONTENT" | grep -q "o_login_auth"; then
    echo "  ✅ Login page contains auth form"
else
    error "Login page missing auth form - possible OWL error"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 5: No SCSS compilation errors
# -----------------------------------------------------------------------------
info "Checking for SCSS errors in logs..."

SCSS_ERRORS=$(docker compose -f "$COMPOSE_FILE" logs --tail=500 odoo 2>/dev/null | \
    grep -ci "scss\|sass\|compile.*error" || echo "0")

if [ "$SCSS_ERRORS" -gt 0 ]; then
    warn "Found $SCSS_ERRORS potential SCSS-related log entries"
    docker compose -f "$COMPOSE_FILE" logs --tail=500 odoo 2>/dev/null | \
        grep -i "scss\|sass\|compile.*error" | tail -5
else
    echo "  ✅ No SCSS compilation errors in recent logs"
fi

# -----------------------------------------------------------------------------
# Check 6: No OWL errors in logs
# -----------------------------------------------------------------------------
info "Checking for OWL errors in logs..."

OWL_ERRORS=$(docker compose -f "$COMPOSE_FILE" logs --tail=500 odoo 2>/dev/null | \
    grep -ci "owl\|component.*error\|template.*error" || echo "0")

if [ "$OWL_ERRORS" -gt 0 ]; then
    warn "Found $OWL_ERRORS potential OWL-related log entries"
    docker compose -f "$COMPOSE_FILE" logs --tail=500 odoo 2>/dev/null | \
        grep -i "owl\|component.*error\|template.*error" | tail -5
else
    echo "  ✅ No OWL errors in recent logs"
fi

# -----------------------------------------------------------------------------
# Check 7: Asset bundle integrity
# -----------------------------------------------------------------------------
info "Checking asset bundle integrity..."

# Get a list of asset bundles from the database
BUNDLE_CHECK=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    odoo shell -d odoo --no-http <<'EOF' 2>/dev/null || echo "error"
try:
    attachments = env['ir.attachment'].search([
        ('url', 'like', '/web/assets/'),
        ('create_date', '>=', '2026-01-01')
    ], limit=10)
    if attachments:
        print(f"found:{len(attachments)}")
    else:
        print("found:0")
except Exception as e:
    print(f"error:{e}")
EOF
)

BUNDLE_CHECK=$(echo "$BUNDLE_CHECK" | tail -1 | tr -d '[:space:]')

if [[ "$BUNDLE_CHECK" == found:* ]]; then
    COUNT="${BUNDLE_CHECK#found:}"
    if [ "$COUNT" -gt 0 ]; then
        echo "  ✅ Found $COUNT asset bundle attachments"
    else
        warn "No recent asset bundles found - may need regeneration"
    fi
else
    warn "Could not verify asset bundles: $BUNDLE_CHECK"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "Assets Verification Summary"
echo "=============================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All asset checks passed!${NC}"
    echo ""
    echo "Assets are properly compiled and accessible."
    exit 0
else
    echo -e "${RED}❌ ${FAILURES} check(s) failed${NC}"
    echo ""
    echo "Asset issues detected. Recommended actions:"
    echo "  1. Run: docker compose exec odoo odoo -d odoo -u web,base --stop-after-init"
    echo "  2. Restart: docker compose restart odoo"
    echo "  3. Check logs: docker compose logs --tail=200 odoo"
    exit 1
fi
