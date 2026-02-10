#!/usr/bin/env bash
# Environment-aware Docker Compose shutdown script
# Usage: ./scripts/down.sh [dev|stage|prod]

set -euo pipefail

ENV="${1:-dev}"

case "$ENV" in
  dev|stage|prod)
    echo "🛑 Stopping Odoo environment: $ENV"
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

# Stop services
echo "📋 Using environment file: $ENV_FILE"
docker compose --env-file "$ENV_FILE" down

echo "✅ Environment '$ENV' stopped successfully"
