#!/bin/bash
# =============================================================================
# Platform Health Check Script
# =============================================================================
# Usage: ./scripts/health.sh
# Returns: 0 if all services healthy, 1 if any service unhealthy
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILURES=0

check_service() {
    local name="$1"
    local check_cmd="$2"

    echo -n "$name: "
    if eval "$check_cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILURES++)) || true
    fi
}

echo "=== Platform Health Check ==="
echo ""

# Nginx
check_service "Nginx" "curl -fsS http://localhost/nginx-health"

# Odoo (via proxy)
check_service "Odoo (proxy)" "curl -fsS http://localhost:8069/web/health"

# Odoo (direct container check)
check_service "Odoo (container)" "docker exec ipai-odoo curl -fsS http://localhost:8069/web/health"

# PostgreSQL
check_service "PostgreSQL" "docker exec ipai-odoo-db pg_isready -U odoo -q"

# Redis
check_service "Redis" "docker exec ipai-odoo-redis redis-cli ping"

# Check for Supabase local (if profile active)
if docker ps --format '{{.Names}}' | grep -q ipai-supabase-postgrest 2>/dev/null; then
    echo ""
    echo "=== Supabase Local Stack ==="
    check_service "PostgREST" "curl -fsS http://localhost:3000/"
fi

echo ""
echo "=== Summary ==="

if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}All services healthy${NC}"
    exit 0
else
    echo -e "${RED}$FAILURES service(s) unhealthy${NC}"
    exit 1
fi
