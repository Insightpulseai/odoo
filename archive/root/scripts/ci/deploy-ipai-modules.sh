#!/bin/bash
set -euo pipefail

# Finance PPM IPAI Module Deployment Script
# XML-RPC based activation

ODOO_URL="http://localhost:8071"
ODOO_DB="odoo_accounting"
ODOO_USER="admin"
ODOO_PASSWORD="${ODOO_ADMIN_PASSWORD}"

echo "=== Finance PPM: IPAI Module Deployment ==="
echo "Odoo URL: $ODOO_URL"
echo "Database: $ODOO_DB"

# IPAI Finance PPM modules
declare -a IPAI_MODULES=(
  "ipai_finance_ppm"
  "ipai_ppm_a1"
  "ipai_close_orchestration"
  "ipai_clarity_ppm_parity"
  "ipai_task_automation"
  "ipai_dashboard_echarts"
  "ipai_bir_schedule"
  "ipai_logframe"
  "ipai_agency_multi"
  "ipai_supabase_sync"
  "ipai_mattermost_notify"
  "ipai_n8n_integration"
  "ipai_approval_workflows"
)

activate_module() {
  local module=$1
  echo ">>> Activating $module..."

  python3 << EOF
import xmlrpc.client

odoo_url = "$ODOO_URL"
db = "$ODOO_DB"
username = "$ODOO_USER"
password = "$ODOO_PASSWORD"

common = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed")
    exit(1)

models = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/object")

# Search for module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', '$module']]])

if not module_ids:
    print(f"❌ Module $module not found")
    exit(1)

# Install module
models.execute_kw(db, uid, password,
    'ir.module.module', 'button_immediate_install',
    [module_ids])

print(f"✅ $module activated successfully")
EOF

  if [ $? -eq 0 ]; then
    return 0
  else
    return 1
  fi
}

# Activate each IPAI module
for module in "${IPAI_MODULES[@]}"; do
  activate_module "$module" || exit 1
  echo ""
done

echo "=== IPAI Module Deployment Complete ==="
echo "Activated ${#IPAI_MODULES[@]} modules successfully"
