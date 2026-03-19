#!/usr/bin/env bash
set -euo pipefail

# Finance PPM Health Check Runner
# Purpose: Execute health check SQL against production or test database
# Usage: ./scripts/finance_ppm_health_check.sh [odoo|odoo_ppm_test]

DB_CONTAINER=${DB_CONTAINER:-odoo-db-1}
DB_NAME=${1:-odoo}
DB_USER=${DB_USER:-odoo}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Finance PPM Health Check"
echo "   Database: $DB_NAME"
echo "   Container: $DB_CONTAINER"
echo ""

docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SCRIPT_DIR/finance_ppm_health_check.sql"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Health check completed successfully"
else
    echo ""
    echo "❌ Health check failed with exit code $exit_code"
fi

exit $exit_code
