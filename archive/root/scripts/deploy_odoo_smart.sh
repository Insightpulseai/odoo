#!/usr/bin/env bash
#
# Smart Odoo Module Deployment Script
# Automatically detects if modules need -i (install) or -u (upgrade)
#
set -euo pipefail

CONTAINER="${ODOO_CONTAINER:-odoo-erp-prod}"
DB="${ODOO_DB:-odoo}"
MODULES="${ODOO_MODULES:-}"

if [ -z "$MODULES" ]; then
  echo "Error: ODOO_MODULES environment variable not set"
  echo "Usage: ODOO_MODULES=module1,module2 $0"
  exit 1
fi

echo "==========================================================================="
echo "Smart Odoo Module Deployment"
echo "==========================================================================="
echo "Container: ${CONTAINER}"
echo "Database:  ${DB}"
echo "Modules:   ${MODULES}"
echo ""

# Function to check module installation status
check_module_status() {
  local module="$1"
  docker exec -i "${CONTAINER}" python3 - <<PYEOF
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        dbname='${DB}',
        user=os.environ.get('PGUSER', 'odoo'),
        password=os.environ.get('PGPASSWORD', ''),
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', '5432')
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT state FROM ir_module_module WHERE name = %s",
        ('${module}',)
    )
    result = cur.fetchone()

    if result is None:
        print('not_found')
    else:
        print(result[0])

    cur.close()
    conn.close()
except Exception as e:
    print(f'error: {e}', file=sys.stderr)
    sys.exit(1)
PYEOF
}

# Split modules into install and upgrade lists
TO_INSTALL=()
TO_UPGRADE=()

echo "Checking module installation status..."
echo "-----------------------------------------------------------------------"

IFS=',' read -ra MODULE_ARRAY <<< "$MODULES"
for module in "${MODULE_ARRAY[@]}"; do
  # Trim whitespace
  module=$(echo "$module" | xargs)

  status=$(check_module_status "$module" 2>&1)

  case "$status" in
    installed)
      echo "  ✅ $module: installed (will upgrade)"
      TO_UPGRADE+=("$module")
      ;;
    uninstalled|to*)
      echo "  📦 $module: uninstalled (will install)"
      TO_INSTALL+=("$module")
      ;;
    not_found)
      echo "  ⚠️  $module: not found in module list (will attempt install)"
      TO_INSTALL+=("$module")
      ;;
    error*)
      echo "  ❌ $module: error checking status: $status"
      echo "     Will attempt install as fallback"
      TO_INSTALL+=("$module")
      ;;
    *)
      echo "  ⚠️  $module: unknown state '$status' (will attempt upgrade)"
      TO_UPGRADE+=("$module")
      ;;
  esac
done

echo ""
echo "==========================================================================="
echo "Deployment Plan"
echo "==========================================================================="

# Build comma-separated lists
INSTALL_LIST=$(IFS=,; echo "${TO_INSTALL[*]}")
UPGRADE_LIST=$(IFS=,; echo "${TO_UPGRADE[*]}")

if [ ${#TO_INSTALL[@]} -gt 0 ]; then
  echo "📦 INSTALL (${#TO_INSTALL[@]} modules): $INSTALL_LIST"
else
  echo "📦 INSTALL: (none)"
fi

if [ ${#TO_UPGRADE[@]} -gt 0 ]; then
  echo "⬆️  UPGRADE (${#TO_UPGRADE[@]} modules): $UPGRADE_LIST"
else
  echo "⬆️  UPGRADE: (none)"
fi

echo ""
read -p "Proceed with deployment? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "==========================================================================="
echo "Executing Deployment"
echo "==========================================================================="

# Install new modules
if [ ${#TO_INSTALL[@]} -gt 0 ]; then
  echo ""
  echo "📦 Installing modules: $INSTALL_LIST"
  echo "-----------------------------------------------------------------------"

  docker exec -i "${CONTAINER}" bash -lc "
    set -euo pipefail
    odoo -c /etc/odoo/odoo.conf -d '${DB}' -i '${INSTALL_LIST}' --stop-after-init
  " || {
    echo "❌ Installation failed!"
    exit 1
  }

  echo "✅ Installation complete"
fi

# Upgrade existing modules
if [ ${#TO_UPGRADE[@]} -gt 0 ]; then
  echo ""
  echo "⬆️  Upgrading modules: $UPGRADE_LIST"
  echo "-----------------------------------------------------------------------"

  docker exec -i "${CONTAINER}" bash -lc "
    set -euo pipefail
    odoo -c /etc/odoo/odoo.conf -d '${DB}' -u '${UPGRADE_LIST}' --stop-after-init
  " || {
    echo "❌ Upgrade failed!"
    exit 1
  }

  echo "✅ Upgrade complete"
fi

# Restart container
echo ""
echo "🔄 Restarting container..."
docker restart "${CONTAINER}"

# Wait for container to be healthy
echo "⏳ Waiting for container to be ready..."
sleep 5

# Show logs
echo ""
echo "==========================================================================="
echo "Container Logs (last 200 lines)"
echo "==========================================================================="
docker logs --tail=200 "${CONTAINER}"

echo ""
echo "==========================================================================="
echo "✅ Deployment Complete"
echo "==========================================================================="
echo ""
echo "To verify module status:"
echo "  docker exec -i ${CONTAINER} psql -U odoo -d ${DB} -c \\"
echo "    \"SELECT name, state, latest_version FROM ir_module_module WHERE name IN ('$(echo "$MODULES" | sed "s/,/','/g")');\""
echo ""
