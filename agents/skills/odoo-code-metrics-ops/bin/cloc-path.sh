#!/usr/bin/env bash
# odoo-code-metrics-ops: Count lines of code for modules in a directory
# Usage: cloc-path.sh <addons-dir>
set -euo pipefail

ADDONS_DIR="${1:?Usage: cloc-path.sh <addons-dir>}"

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-18-dev/bin/python}"

echo "Running cloc for path ${ADDONS_DIR}"
"${PYTHON}" "${ODOO_BIN}" cloc --path "${ADDONS_DIR}"
