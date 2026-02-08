#!/usr/bin/env bash
# Smoke Test: Verify Odoo docker containers are operational
# Usage: ./scripts/smoke_odoo_container.sh

set -euo pipefail

echo "🔍 Smoke Test: Odoo Docker Container Health"
echo "============================================="

# Auto-detect service names using compose_vars.sh if available
if [[ -f "$(dirname "$0")/compose_vars.sh" ]]; then
    source "$(dirname "$0")/compose_vars.sh" --quiet
else
    # Fallback to common service names
    APP_SVC="${APP_SVC:-odoo-core}"
    DB_SVC="${DB_SVC:-postgres}"
fi

echo "Detected services: APP=$APP_SVC, DB=$DB_SVC"
echo ""

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo "⚠️  SKIP: Docker not available (CI environment may not support docker)"
    exit 0
fi

# Check if compose file exists
if [[ ! -f docker-compose.yml ]]; then
    echo "⚠️  SKIP: No docker-compose.yml found"
    exit 0
fi

# Check container status
echo "Checking container status..."

# Check app container
if docker compose ps "$APP_SVC" 2>/dev/null | grep -q "Up"; then
    echo "✅ PASS: $APP_SVC container is running"
else
    echo "❌ FAIL: $APP_SVC container is not running"
    docker compose ps "$APP_SVC" 2>/dev/null || echo "Container not found"
    exit 1
fi

# Check database container
if docker compose ps "$DB_SVC" 2>/dev/null | grep -q "Up"; then
    echo "✅ PASS: $DB_SVC container is running"
else
    echo "❌ FAIL: $DB_SVC container is not running"
    docker compose ps "$DB_SVC" 2>/dev/null || echo "Container not found"
    exit 1
fi

# Check health status if available
echo ""
echo "Checking health status..."

APP_HEALTH=$(docker compose ps "$APP_SVC" 2>/dev/null | grep "$APP_SVC" | awk '{print $NF}')
DB_HEALTH=$(docker compose ps "$DB_SVC" 2>/dev/null | grep "$DB_SVC" | awk '{print $NF}')

echo "  $APP_SVC: $APP_HEALTH"
echo "  $DB_SVC: $DB_HEALTH"

echo ""
echo "✅ All container checks passed"
