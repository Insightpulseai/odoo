#!/usr/bin/env bash
# ============================================================================
# deploy_powerbi_views.sh — Create pbi.* views on Odoo PostgreSQL
# ============================================================================
# Usage:
#   ./deploy_powerbi_views.sh                    # uses defaults (odoo_dev)
#   ./deploy_powerbi_views.sh odoo               # target production DB
#   DB_HOST=localhost DB_USER=tbwa ./deploy_powerbi_views.sh  # local dev
#
# Prerequisites:
#   - psql client installed
#   - Access to the target PostgreSQL server
#   - For Azure: credentials via Key Vault or .pgpass
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="${SCRIPT_DIR}/../data/powerbi_views.sql"

# Defaults — Azure PostgreSQL Flexible Server
DB_NAME="${1:-odoo_dev}"
DB_HOST="${DB_HOST:-ipai-odoo-dev-pg.postgres.database.azure.com}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo_admin}"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Finance PPM — Power BI Views Deployment                ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Host:     ${DB_HOST}"
echo "║  Port:     ${DB_PORT}"
echo "║  Database: ${DB_NAME}"
echo "║  User:     ${DB_USER}"
echo "║  SQL:      ${SQL_FILE}"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ ! -f "${SQL_FILE}" ]; then
    echo "ERROR: SQL file not found: ${SQL_FILE}"
    exit 1
fi

echo "Creating pbi schema and views..."
psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -f "${SQL_FILE}" \
    -v ON_ERROR_STOP=1

echo ""
echo "Verifying views..."
VIEW_COUNT=$(psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -t -A -c "SELECT count(*) FROM information_schema.views WHERE table_schema = 'pbi'")

echo "Views created in pbi schema: ${VIEW_COUNT}"

if [ "${VIEW_COUNT}" -ge 10 ]; then
    echo "✓ All views deployed successfully (${VIEW_COUNT}/10+)"
else
    echo "⚠ Expected ≥10 views, got ${VIEW_COUNT}. Check for errors above."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Power BI Connection Parameters:"
echo "  Server:   ${DB_HOST}"
echo "  Database: ${DB_NAME}"
echo "  Schema:   pbi"
echo "  Auth:     Azure AD (preferred) or Basic"
echo ""
echo "In Power BI Desktop:"
echo "  1. Get Data → PostgreSQL database"
echo "  2. Server: ${DB_HOST}"
echo "  3. Database: ${DB_NAME}"
echo "  4. Advanced → SQL: SELECT * FROM pbi.<view_name>"
echo "  5. Import theme: FinancePPM_OKR_Theme.json"
echo "  6. Build visuals per FinancePPM_OKR_ReportLayout.json"
echo "═══════════════════════════════════════════════════════════"
