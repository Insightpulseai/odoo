#!/usr/bin/env bash
#
# Check Odoo Module Installation Status
# Usage: ./check_module_status.sh [module1,module2,...]
#
set -euo pipefail

CONTAINER="${ODOO_CONTAINER:-odoo-erp-prod}"
DB="${ODOO_DB:-odoo}"
MODULES="${1:-ipai_platform_theme,ipai_finance_ppm,ipai_finance_ppm_umbrella}"

echo "==========================================================================="
echo "Odoo Module Status Check"
echo "==========================================================================="
echo "Container: ${CONTAINER}"
echo "Database:  ${DB}"
echo "Modules:   ${MODULES}"
echo ""

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

    modules = '${MODULES}'.split(',')

    print("=" * 80)
    print(f"{'Module':<40} {'State':<15} {'Version':<20}")
    print("=" * 80)

    for module in modules:
        module = module.strip()
        cur.execute(
            """
            SELECT name, state, latest_version
            FROM ir_module_module
            WHERE name = %s
            """,
            (module,)
        )
        result = cur.fetchone()

        if result is None:
            print(f"{module:<40} {'NOT FOUND':<15} {'-':<20}")
        else:
            name, state, version = result
            # Add emoji indicators
            emoji = {
                'installed': '✅',
                'uninstalled': '📦',
                'to install': '⏳',
                'to upgrade': '⬆️',
                'to remove': '🗑️'
            }.get(state, '⚠️')

            print(f"{name:<40} {emoji} {state:<12} {version or 'N/A':<20}")

    print("=" * 80)

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

echo ""
echo "Legend:"
echo "  ✅ installed   - Module is installed and running"
echo "  📦 uninstalled - Module is available but not installed (use -i)"
echo "  ⏳ to install  - Module is queued for installation"
echo "  ⬆️  to upgrade  - Module has pending upgrade"
echo "  ⚠️  other state - Check module manually"
echo ""
