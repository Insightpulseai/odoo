#!/usr/bin/env bash
# Environment-aware Docker Compose startup script
# Usage: ./scripts/up.sh [dev|stage|prod]

set -euo pipefail

ENV="${1:-dev}"

case "$ENV" in
  dev|stage|prod)
    echo "🚀 Starting Odoo environment: $ENV"
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

# Load project name from ops/compose/project.env
export $(grep -v '^#' ops/compose/project.env | xargs)

# Start services with environment-specific config
echo "📋 Using environment file: $ENV_FILE"
docker compose --env-file "$ENV_FILE" up -d

echo "✅ Environment '$ENV' started successfully"
echo ""
echo "Database: odoo_${ENV}"
echo "Odoo URL: http://localhost:$(grep ODOO_PORT "$ENV_FILE" | cut -d= -f2)"
echo ""
echo "View logs: docker compose logs -f odoo-app"
echo "Stop: ./scripts/down.sh $ENV"
