#!/usr/bin/env bash
# Smoke Test: Verify Odoo docker containers are operational
# Usage: ./scripts/smoke_odoo_container.sh

set -euo pipefail

# GitHub Actions annotation helpers
notice() { echo "::notice::$*"; }
warn() { echo "::warning::$*"; }

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

# Check if docker command is available
if ! command -v docker &> /dev/null; then
    notice "SKIPPED: docker command not available in this environment"
    exit 0
fi

# Check if docker daemon is reachable
if ! docker info >/dev/null 2>&1; then
    notice "SKIPPED: docker daemon not reachable (may require docker service running)"
    exit 0
fi

# Check if compose file exists
if [[ ! -f docker-compose.yml ]]; then
    notice "SKIPPED: docker-compose.yml not found in current directory"
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
