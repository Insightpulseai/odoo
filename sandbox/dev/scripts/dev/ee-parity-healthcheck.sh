#!/usr/bin/env bash
# scripts/dev/ee-parity-healthcheck.sh
#
# Validate that EE-parity modules are installed and up-to-date
#
# Exit codes:
#   0  = All modules installed and up-to-date
#   10 = Missing modules (uninstalled)
#   11 = Modules need upgrade (to upgrade state)
#   12 = Environment validation failed

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# 1. VALIDATE ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "ERROR: .env not found at $ROOT_DIR/.env" >&2
  exit 12
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
  exit 12
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
echo "║   EE Parity Healthcheck                    ║"
echo "╚════════════════════════════════════════════╝"
echo
echo "Database: $ODOO_DB_NAME"
echo "Container: $ODOO_CONTAINER"
echo

# Execute query and capture output
QUERY_OUTPUT=$(docker compose exec -T "$ODOO_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$ODOO_DB_NAME" -c "$SQL" 2>&1)

# Display query results
echo "$QUERY_OUTPUT"

# ═══════════════════════════════════════════════════════════════════════════════
# 5. SUMMARY STATISTICS & EXIT CODE DETERMINATION
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
SUMMARY_OUTPUT=$(docker compose exec -T "$ODOO_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$ODOO_DB_NAME" -c "$SUMMARY_SQL" 2>&1)

echo "$SUMMARY_OUTPUT"

# Count modules by state
MISSING_COUNT=$(echo "$SUMMARY_OUTPUT" | grep -c "uninstalled" || true)
UPGRADE_COUNT=$(echo "$SUMMARY_OUTPUT" | grep -c "to upgrade" || true)
TO_INSTALL_COUNT=$(echo "$SUMMARY_OUTPUT" | grep -c "to install" || true)

echo
echo "Legend:"
echo "  ✅ installed     - Module is active and up-to-date"
echo "  ⬆️  to upgrade   - Module needs upgrade"
echo "  📦 to install   - Module queued for installation"
echo "  ❌ uninstalled  - Module not installed"
echo

# ═══════════════════════════════════════════════════════════════════════════════
# 6. EXIT CODE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$MISSING_COUNT" -gt 0 ] || [ "$TO_INSTALL_COUNT" -gt 0 ]; then
  echo "❌ HEALTHCHECK FAILED: $MISSING_COUNT uninstalled modules, $TO_INSTALL_COUNT queued"
  echo "   Run: ./scripts/dev/install-ee-parity-modules.sh"
  exit 10
elif [ "$UPGRADE_COUNT" -gt 0 ]; then
  echo "⚠️  HEALTHCHECK WARNING: $UPGRADE_COUNT modules need upgrade"
  echo "   Run: ./scripts/dev/install-ee-parity-modules.sh"
  exit 11
else
  echo "✅ HEALTHCHECK PASSED: All EE-parity modules installed and up-to-date"
  exit 0
fi
