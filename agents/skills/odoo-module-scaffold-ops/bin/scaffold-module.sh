#!/usr/bin/env bash
# odoo-module-scaffold-ops: Scaffold a new IPAI module
# Usage: scaffold-module.sh <module_name>
set -euo pipefail

MODULE_NAME="${1:?Usage: scaffold-module.sh <module_name> (e.g., ipai_finance_budget)}"

# Validate naming convention
if [[ ! "${MODULE_NAME}" =~ ^ipai_[a-z]+_[a-z_]+$ ]]; then
  echo "ERROR: Module name must match ipai_<domain>_<feature> pattern"
  echo "Examples: ipai_finance_ppm, ipai_ai_tools, ipai_auth_oidc"
  exit 1
fi

DEST="${DEST:-addons/ipai}"
ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-18-dev/bin/python}"

echo "Scaffolding ${MODULE_NAME} in ${DEST}/"
"${PYTHON}" "${ODOO_BIN}" scaffold "${MODULE_NAME}" "${DEST}"

echo "Module scaffolded at ${DEST}/${MODULE_NAME}/"
echo "Next: update __manifest__.py with version 19.0.1.0.0, license LGPL-3, and dependencies"
ls -la "${DEST}/${MODULE_NAME}/"
