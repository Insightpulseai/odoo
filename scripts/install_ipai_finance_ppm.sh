#!/usr/bin/env bash
set -euo pipefail

DB_NAME="odoo"
ODOO_BIN="${ODOO_BIN:-./odoo-bin}"
MODULE="ipai_finance_ppm"

usage() {
  echo "Usage: $0 [-d db_name] [-m module_name]"
  exit 1
}

while getopts ":d:m:" opt; do
  case "$opt" in
    d) DB_NAME="$OPTARG" ;;
    m) MODULE="$OPTARG" ;;
    *) usage ;;
  esac
done

echo "▶️ Preparing to install module: ${MODULE} (DB: ${DB_NAME})"

# 1) Pre-install snapshot
scripts/pre_install_snapshot.sh "${MODULE}"

# 2) Install with full debug logging
LOG_FILE="logs/install_${MODULE}_$(date +%Y%m%d%H%M%S).log"
mkdir -p logs

echo "▶️ Running Odoo installer..."
echo "   Logging to: ${LOG_FILE}"

${ODOO_BIN} \
  -d "${DB_NAME}" \
  -i "${MODULE}" \
  --stop-after-init \
  --log-level=debug \
  --log-file="${LOG_FILE}"

echo "✅ Module '${MODULE}' installed successfully."
