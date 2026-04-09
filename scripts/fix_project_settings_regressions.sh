#!/usr/bin/env bash
# Fix two Project settings regressions:
#   A) timeline view type crash (install ipai_project_timeline_fix)
#   B) res.config.settings stale view (update base_tier_validation)
#
# Usage: ./scripts/fix_project_settings_regressions.sh

set -euo pipefail

PYTHON="${HOME}/.pyenv/versions/odoo-18-dev/bin/python"
ODOO_BIN="vendor/odoo/odoo-bin"
DB="odoo_dev"
ADDONS_PATH="vendor/odoo/addons,addons/ipai,addons/oca/project,addons/oca/web,addons/oca/server-ux"

echo "=== Fix A: Install ipai_project_timeline_fix ==="
"${PYTHON}" "${ODOO_BIN}" \
    --database="${DB}" \
    --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
    --addons-path="${ADDONS_PATH}" \
    --init=ipai_project_timeline_fix \
    --stop-after-init \
    --no-http \
    2>&1 | tail -5

echo ""
echo "=== Fix B: Update base_tier_validation (re-sync stale view 2904) ==="
"${PYTHON}" "${ODOO_BIN}" \
    --database="${DB}" \
    --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
    --addons-path="${ADDONS_PATH}" \
    --update=base_tier_validation \
    --stop-after-init \
    --no-http \
    2>&1 | tail -5

echo ""
echo "=== Verification ==="
psql -d "${DB}" -t -A -c "
SELECT 'timeline_fix: ' || state FROM ir_module_module WHERE name = 'ipai_project_timeline_fix'
UNION ALL
SELECT 'action_398_view_mode: ' || view_mode FROM ir_act_window WHERE id = 398
UNION ALL
SELECT 'stale_fields: ' || count(*)::text
FROM (
    SELECT 1 FROM ir_ui_view
    WHERE id = 2904
    AND arch_db::text LIKE '%module_base_tier_validation_forward%'
) x;
"

echo ""
echo "Done. Restart Odoo to verify in browser."
