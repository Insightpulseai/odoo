#!/usr/bin/env bash
# Odoo CE/OCA Test Runner
# Runs Odoo tests with configurable modules and logging

set -euo pipefail

DB_NAME="${DB_NAME:-odoo}"
ODOO_MODULES="${ODOO_MODULES:-all}"
LOG_LEVEL="${LOG_LEVEL:-info}"
ADDONS_PATH="${ADDONS_PATH:-addons,oca}"

echo "Running Odoo tests for modules: ${ODOO_MODULES}"
echo "Database: ${DB_NAME}"
echo "Log level: ${LOG_LEVEL}"
echo "Addons path: ${ADDONS_PATH}"

odoo \
  -d "${DB_NAME}" \
  -i "${ODOO_MODULES}" \
  --stop-after-init \
  --log-level="${LOG_LEVEL}" \
  --test-enable \
  --addons-path="${ADDONS_PATH}"
