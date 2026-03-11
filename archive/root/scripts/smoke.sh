#!/usr/bin/env bash
# Environment health check script
# Usage: ./scripts/smoke.sh [dev|stage|prod]

set -euo pipefail

ENV="${1:-dev}"

case "$ENV" in
  dev|stage|prod)
    echo "🔍 Verifying Odoo environment: $ENV"
    ;;
  *)
    echo "❌ Invalid environment: $ENV"
    echo "Usage: $0 [dev|stage|prod]"
    exit 1
    ;;
esac

ENV_FILE="ops/compose/${ENV}.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ Environment file not found: $ENV_FILE"
  exit 1
fi

# Extract configuration
ODOO_DB=$(grep ODOO_DB "$ENV_FILE" | cut -d= -f2)
ODOO_PORT=$(grep ODOO_PORT "$ENV_FILE" | cut -d= -f2)
POSTGRES_PORT=$(grep POSTGRES_PORT "$ENV_FILE" | cut -d= -f2)

echo ""
echo "Environment Configuration:"
echo "  Database: $ODOO_DB"
echo "  Odoo Port: $ODOO_PORT"
echo "  PostgreSQL Port: $POSTGRES_PORT"
echo ""

# Check container status
echo "📦 Checking container status..."
if docker compose ps | grep -q "odoo-app.*Up"; then
  echo "  ✅ odoo-app is running"
else
  echo "  ❌ odoo-app is not running"
  exit 1
fi

if docker compose ps | grep -q "odoo-db.*Up"; then
  echo "  ✅ odoo-db is running"
else
  echo "  ❌ odoo-db is not running"
  exit 1
fi

# Check PostgreSQL connectivity
echo ""
echo "🔌 Checking PostgreSQL connectivity..."
if docker compose exec -T postgres psql -U odoo -d "$ODOO_DB" -c "SELECT version();" > /dev/null 2>&1; then
  echo "  ✅ PostgreSQL connection successful"
  echo "  Database '$ODOO_DB' is accessible"
else
  echo "  ❌ PostgreSQL connection failed"
  exit 1
fi

# Check Odoo HTTP endpoint
echo ""
echo "🌐 Checking Odoo HTTP endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${ODOO_PORT}/web" || echo "000")

if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "303" ]]; then
  echo "  ✅ Odoo is responding (HTTP $HTTP_CODE)"
  echo "  URL: http://localhost:${ODOO_PORT}"
else
  echo "  ❌ Odoo is not responding (HTTP $HTTP_CODE)"
  exit 1
fi

# Check Odoo version
echo ""
echo "📌 Odoo version:"
docker compose exec -T app odoo --version | head -n1

echo ""
echo "✅ All health checks passed for environment '$ENV'"
echo ""
echo "Access Odoo at: http://localhost:${ODOO_PORT}"
