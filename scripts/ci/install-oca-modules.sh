#!/bin/bash
set -euo pipefail

# Finance PPM OCA Module Installation Script
# Sequential installation with validation

ODOO_DB="odoo_accounting"
ODOO_CONTAINER="odoo-accounting"

echo "=== Finance PPM: OCA Module Installation ==="
echo "Database: $ODOO_DB"
echo "Container: $ODOO_CONTAINER"

# OCA modules in dependency order
declare -a OCA_MODULES=(
  "account_financial_report"
  "account_asset_management"
  "account_cutoff_accrual_order_base"
  "account_move_reversal"
  "hr_expense_advance_clearing"
  "account_multicurrency_revaluation"
  "account_intercompany"
  "project_wip"
)

install_module() {
  local module=$1
  echo ">>> Installing $module..."

  docker exec $ODOO_CONTAINER odoo-bin \
    -d $ODOO_DB \
    -i $module \
    --stop-after-init \
    --log-level=info

  if [ $? -eq 0 ]; then
    echo "✅ $module installed successfully"
    return 0
  else
    echo "❌ $module installation failed"
    return 1
  fi
}

validate_module() {
  local module=$1
  echo ">>> Validating $module..."

  docker exec $ODOO_CONTAINER odoo-bin shell -d $ODOO_DB << EOF
env = self.env
module_obj = env['ir.module.module'].search([('name', '=', '$module')])
if module_obj and module_obj.state == 'installed':
    print('✅ $module validation passed')
    exit(0)
else:
    print('❌ $module validation failed - state:', module_obj.state if module_obj else 'NOT FOUND')
    exit(1)
EOF
}

# Install each module sequentially
for module in "${OCA_MODULES[@]}"; do
  install_module "$module" || exit 1
  validate_module "$module" || exit 1
  echo ""
done

echo "=== OCA Module Installation Complete ==="
echo "Installed ${#OCA_MODULES[@]} modules successfully"
