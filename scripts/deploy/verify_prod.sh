#!/bin/bash
# =============================================================================
# Production Verification Script
# =============================================================================
# Usage: ./scripts/deploy/verify_prod.sh [BASE_URL]
#
# Verifies production deployment health:
# - Container status
# - Internal health endpoints
# - External health endpoints (if accessible)
# - Database connectivity
# - Longpolling route
# =============================================================================

set -euo pipefail

BASE_URL="${1:-https://erp.insightpulseai.net}"
COMPOSE_FILE="deploy/docker-compose.prod.yml"
SHIP_VERSION="1.1.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Output helpers
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

FAILURES=0
WARNINGS=0

echo "=============================================="
echo "Production Verification - Ship v${SHIP_VERSION}"
echo "=============================================="
echo "Base URL: ${BASE_URL}"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# -----------------------------------------------------------------------------
# Check 1: Container Status
# -----------------------------------------------------------------------------
info "Checking container status..."

ODOO_STATUS=$(docker compose -f "$COMPOSE_FILE" ps odoo --format '{{.Status}}' 2>/dev/null || echo "not found")
if [[ "$ODOO_STATUS" == *"Up"* ]]; then
    pass "Odoo container: ${ODOO_STATUS}"
else
    fail "Odoo container: ${ODOO_STATUS}"
    FAILURES=$((FAILURES + 1))
fi

DB_STATUS=$(docker compose -f "$COMPOSE_FILE" ps db --format '{{.Status}}' 2>/dev/null || echo "not found")
if [[ "$DB_STATUS" == *"Up"* ]]; then
    pass "Database container: ${DB_STATUS}"
else
    fail "Database container: ${DB_STATUS}"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 2: Internal Health (from inside container)
# -----------------------------------------------------------------------------
info "Checking internal health..."

INTERNAL_LOGIN=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/login 2>/dev/null || echo "000")

if [ "$INTERNAL_LOGIN" == "200" ] || [ "$INTERNAL_LOGIN" == "303" ]; then
    pass "Internal /web/login: $INTERNAL_LOGIN"
else
    fail "Internal /web/login: $INTERNAL_LOGIN (expected 200 or 303)"
    FAILURES=$((FAILURES + 1))
fi

INTERNAL_HEALTH=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/health 2>/dev/null || echo "000")

if [ "$INTERNAL_HEALTH" == "200" ]; then
    pass "Internal /web/health: $INTERNAL_HEALTH"
else
    fail "Internal /web/health: $INTERNAL_HEALTH (expected 200)"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 3: External Health (from edge)
# -----------------------------------------------------------------------------
info "Checking external health..."

EXTERNAL_LOGIN=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 \
    "${BASE_URL}/web/login" 2>/dev/null || echo "000")

if [ "$EXTERNAL_LOGIN" == "200" ] || [ "$EXTERNAL_LOGIN" == "303" ]; then
    pass "External /web/login: $EXTERNAL_LOGIN"
else
    warn "External /web/login: $EXTERNAL_LOGIN (may be network issue)"
    WARNINGS=$((WARNINGS + 1))
fi

EXTERNAL_HEALTH=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 \
    "${BASE_URL}/web/health" 2>/dev/null || echo "000")

if [ "$EXTERNAL_HEALTH" == "200" ]; then
    pass "External /web/health: $EXTERNAL_HEALTH"
else
    warn "External /web/health: $EXTERNAL_HEALTH (may be network issue)"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Check 4: Database Connectivity
# -----------------------------------------------------------------------------
info "Checking database connectivity..."

DB_READY=$(docker compose -f "$COMPOSE_FILE" exec -T db \
    pg_isready -U odoo -d odoo 2>/dev/null || echo "failed")

if [[ "$DB_READY" == *"accepting connections"* ]]; then
    pass "Database accepting connections"
else
    fail "Database not ready: $DB_READY"
    FAILURES=$((FAILURES + 1))
fi

# -----------------------------------------------------------------------------
# Check 5: Longpolling Route
# -----------------------------------------------------------------------------
info "Checking longpolling route..."

# Internal longpoll check
INTERNAL_POLL=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' http://localhost:8072/longpolling/poll 2>/dev/null || echo "000")

if [ "$INTERNAL_POLL" == "200" ] || [ "$INTERNAL_POLL" == "400" ]; then
    pass "Internal longpolling: $INTERNAL_POLL (responding)"
else
    warn "Internal longpolling: $INTERNAL_POLL (may need workers config)"
    WARNINGS=$((WARNINGS + 1))
fi

# External longpoll check
EXTERNAL_POLL=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 \
    "${BASE_URL}/longpolling/poll" 2>/dev/null || echo "000")

if [ "$EXTERNAL_POLL" == "200" ] || [ "$EXTERNAL_POLL" == "400" ]; then
    pass "External longpolling: $EXTERNAL_POLL (route configured)"
else
    warn "External longpolling: $EXTERNAL_POLL (check nginx config)"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Check 6: Assets
# -----------------------------------------------------------------------------
info "Checking assets..."

ASSETS=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    curl -sS -o /dev/null -w '%{http_code}' \
    http://localhost:8069/web/assets/debug/web.assets_backend.js 2>/dev/null || echo "000")

if [ "$ASSETS" == "200" ]; then
    pass "Backend assets: $ASSETS"
else
    warn "Backend assets: $ASSETS (may need asset regeneration)"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Check 7: Ship Modules Installed
# -----------------------------------------------------------------------------
info "Checking ship modules..."

MODULES_CHECK=$(docker compose -f "$COMPOSE_FILE" exec -T odoo \
    odoo shell -d odoo --no-http <<'EOF' 2>/dev/null || echo "error"
modules = ['ipai_theme_aiux', 'ipai_aiux_chat', 'ipai_ask_ai', 'ipai_document_ai', 'ipai_expense_ocr']
installed = 0
for m in modules:
    mod = env['ir.module.module'].search([('name', '=', m), ('state', '=', 'installed')])
    if mod:
        installed += 1
print(f"installed:{installed}/5")
EOF
)

MODULES_CHECK=$(echo "$MODULES_CHECK" | tail -1 | tr -d '[:space:]')

if [ "$MODULES_CHECK" == "installed:5/5" ]; then
    pass "Ship modules: 5/5 installed"
else
    warn "Ship modules: $MODULES_CHECK"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Generate Proof
# -----------------------------------------------------------------------------
info "Generating proof artifact..."

DEPLOY_ID="deploy-$(date +%Y%m%d-%H%M%S)"
GIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

mkdir -p proofs

cat > "proofs/${DEPLOY_ID}.json" <<EOF
{
  "deploy_id": "${DEPLOY_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "ship_version": "${SHIP_VERSION}",
  "git_sha": "${GIT_SHA}",
  "base_url": "${BASE_URL}",
  "checks": {
    "odoo_container": "${ODOO_STATUS}",
    "db_container": "${DB_STATUS}",
    "internal_login": "${INTERNAL_LOGIN}",
    "internal_health": "${INTERNAL_HEALTH}",
    "external_login": "${EXTERNAL_LOGIN}",
    "external_health": "${EXTERNAL_HEALTH}",
    "db_connectivity": "${DB_READY}",
    "longpolling_internal": "${INTERNAL_POLL}",
    "longpolling_external": "${EXTERNAL_POLL}",
    "assets": "${ASSETS}",
    "modules": "${MODULES_CHECK}"
  },
  "failures": ${FAILURES},
  "warnings": ${WARNINGS},
  "status": "$([ $FAILURES -eq 0 ] && echo 'success' || echo 'failed')"
}
EOF

pass "Proof saved: proofs/${DEPLOY_ID}.json"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "Verification Summary"
echo "=============================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) - review above${NC}"
    fi
    echo ""
    echo "Deployment is healthy and ready for traffic."
    exit 0
else
    echo -e "${RED}❌ ${FAILURES} critical check(s) failed${NC}"
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "Deployment has issues. Review errors above."
    echo "Consider rollback if issues persist."
    exit 1
fi
