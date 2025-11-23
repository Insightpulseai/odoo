#!/usr/bin/env bash
# Odoo CE/OCA Test Runner
# Runs Odoo tests with configurable modules and logging

set -euo pipefail

DB_NAME="${DB_NAME:-odoo}"
ODOO_MODULES="${ODOO_MODULES:-all}"
LOG_LEVEL="${LOG_LEVEL:-info}"
ADDONS_PATH="${ADDONS_PATH:-addons,oca}"
ODOO_BIN="${ODOO_BIN:-odoo-bin}"  # Can be overridden for CI

echo "Running Odoo tests for modules: ${ODOO_MODULES}"
echo "Database: ${DB_NAME}"
echo "Log level: ${LOG_LEVEL}"
echo "Addons path: ${ADDONS_PATH}"
echo "Odoo binary: ${ODOO_BIN}"

# Detect odoo-bin location if not specified
if [ "${ODOO_BIN}" == "odoo-bin" ]; then
  # Try common locations
  if [ -f "/tmp/odoo/odoo-bin" ]; then
    ODOO_BIN="python /tmp/odoo/odoo-bin"
  elif command -v odoo-bin &> /dev/null; then
    ODOO_BIN="odoo-bin"
  elif command -v odoo &> /dev/null; then
    ODOO_BIN="odoo"
  else
    echo "Error: Could not find odoo or odoo-bin"
    echo "Please set ODOO_BIN environment variable"
    exit 1
  fi
fi

${ODOO_BIN} \
  -d "${DB_NAME}" \
  -i "${ODOO_MODULES}" \
  --stop-after-init \
  --log-level="${LOG_LEVEL}" \
  --test-enable \
  --addons-path="${ADDONS_PATH}"
