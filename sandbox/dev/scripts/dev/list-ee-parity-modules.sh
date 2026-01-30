#!/usr/bin/env bash
# scripts/dev/list-ee-parity-modules.sh
#
# List EE-parity module installation status from Odoo database
#
# Usage:
#   ./scripts/dev/list-ee-parity-modules.sh
#
# Environment variables (from .env):
#   ODOO_DB_NAME                  - Database name
#   ODOO_EE_PARITY_OCA_MODULES    - Comma-separated OCA modules
#   ODOO_EE_PARITY_IPAI_MODULES   - Comma-separated IPAI modules
#   ODOO_CONTAINER                - Docker container name (default: odoo-dev)
#   POSTGRES_USER                 - PostgreSQL user (default: odoo)

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# 1. VALIDATE ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "ERROR: .env not found at $ROOT_DIR/.env" >&2
  exit 1
fi

# Load environment variables
set -a
# shellcheck source=/dev/null
. .env
set +a

# Required variables
: "${ODOO_DB_NAME:?ODOO_DB_NAME must be set in .env}"
: "${ODOO_EE_PARITY_OCA_MODULES:?ODOO_EE_PARITY_OCA_MODULES must be set in .env}"
: "${ODOO_EE_PARITY_IPAI_MODULES:?ODOO_EE_PARITY_IPAI_MODULES must be set in .env}"

# Optional with defaults
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-dev}"
POSTGRES_USER="${POSTGRES_USER:-odoo}"

# ═══════════════════════════════════════════════════════════════════════════════
# 2. NORMALIZE MODULE LIST
# ═══════════════════════════════════════════════════════════════════════════════

ALL_MODULES_RAW="${ODOO_EE_PARITY_OCA_MODULES},${ODOO_EE_PARITY_IPAI_MODULES}"
ALL_MODULES="$(echo "$ALL_MODULES_RAW" | tr -d '[:space:]' | sed 's/,,*/,/g;s/^,//;s/,$//')"

# Convert to SQL IN clause format: 'module1','module2','module3'
SQL_MODULE_LIST="$(echo "$ALL_MODULES" | sed "s/,/','/g")"

# ═══════════════════════════════════════════════════════════════════════════════
# 3. VERIFY CONTAINER IS RUNNING
# ═══════════════════════════════════════════════════════════════════════════════

if ! docker compose ps "$ODOO_CONTAINER" --services --filter "status=running" | grep -q "$ODOO_CONTAINER"; then
  echo "ERROR: Container '$ODOO_CONTAINER' is not running" >&2
  echo "Start it with: docker compose up -d $ODOO_CONTAINER" >&2
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. QUERY MODULE STATUS
# ═══════════════════════════════════════════════════════════════════════════════

SQL="
SELECT
  name,
  state,
  CASE
    WHEN state = 'installed' THEN '✅'
    WHEN state = 'to upgrade' THEN '⬆️'
    WHEN state = 'to install' THEN '📦'
    WHEN state = 'uninstalled' THEN '❌'
    ELSE '⚠️'
  END as status
FROM ir_module_module
WHERE name IN ('$SQL_MODULE_LIST')
ORDER BY
  CASE state
    WHEN 'installed' THEN 1
    WHEN 'to upgrade' THEN 2
    WHEN 'to install' THEN 3
    WHEN 'uninstalled' THEN 4
    ELSE 5
  END,
  name;
"

echo "╔════════════════════════════════════════════╗"
echo "║   EE Parity Modules Status                 ║"
echo "╚════════════════════════════════════════════╝"
echo
echo "Database: $ODOO_DB_NAME"
echo "Container: $ODOO_CONTAINER"
echo

docker compose exec -T "$ODOO_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$ODOO_DB_NAME" -c "$SQL"

# ═══════════════════════════════════════════════════════════════════════════════
# 5. SUMMARY STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

SUMMARY_SQL="
SELECT
  state,
  COUNT(*) as count
FROM ir_module_module
WHERE name IN ('$SQL_MODULE_LIST')
GROUP BY state
ORDER BY state;
"

echo
echo "Summary:"
docker compose exec -T "$ODOO_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$ODOO_DB_NAME" -c "$SUMMARY_SQL"

echo
echo "Legend:"
echo "  ✅ installed     - Module is active"
echo "  ⬆️  to upgrade   - Module needs upgrade"
echo "  📦 to install   - Module queued for installation"
echo "  ❌ uninstalled  - Module not installed"
