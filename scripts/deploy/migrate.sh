#!/bin/bash
set -e

ENV=$1
MODULES=$2

if [[ -z "$ENV" ]]; then
  echo "Usage: ./migrate.sh <env> [modules]"
  exit 1
fi

# Use -u all if no modules specified
MODULES_FLAG="-u ${MODULES:-all}"

echo "🔄 Running migrations for $ENV on modules: ${MODULES:-all}..."

# Execute odoo-bin update inside the container
docker compose -f docker/compose/$ENV.yml exec odoo-$ENV odoo $MODULES_FLAG --stop-after-init --log-level=info

echo "✅ Migrations complete!"
