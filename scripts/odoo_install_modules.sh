#!/usr/bin/env bash
# =============================================================================
# Install Odoo modules from an install set file.
#
# Usage:
#   ./scripts/odoo_install_modules.sh config/install_sets/ppm_parity_autogen.txt
#   DB_NAME=odoo_core ./scripts/odoo_install_modules.sh config/install_sets/mega_parity_autogen.txt
#
# Reads a .txt file (one module per line, comments allowed), builds a
# comma-separated list, and runs odoo-bin -i with --stop-after-init.
# =============================================================================
set -euo pipefail

DB_NAME="${DB_NAME:-odoo}"
SET_FILE="${1:?Usage: $0 <set_file.txt>}"

if [[ ! -f "$SET_FILE" ]]; then
    echo "ERROR: set file not found: $SET_FILE" >&2
    exit 1
fi

MODULES="$(grep -vE '^\s*#' "$SET_FILE" | sed '/^\s*$/d' | paste -sd, -)"
if [[ -z "$MODULES" ]]; then
    echo "ERROR: no modules found in $SET_FILE" >&2
    exit 1
fi

COUNT="$(echo "$MODULES" | tr ',' '\n' | wc -l)"

echo "================================================================================"
echo "Install Set: $SET_FILE"
echo "Database:    $DB_NAME"
echo "Modules:     $COUNT"
echo "================================================================================"
echo "$MODULES" | tr ',' '\n' | sed 's/^/  - /'
echo ""

echo ">>> Updating base..."
odoo-bin -d "$DB_NAME" --stop-after-init -u base --log-level=warn

echo ">>> Installing modules..."
odoo-bin -d "$DB_NAME" --stop-after-init -i "$MODULES" --log-level=warn

echo ""
echo "OK: install completed ($COUNT modules)"
