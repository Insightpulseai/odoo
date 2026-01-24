#!/usr/bin/env bash
set -euo pipefail

# OCA Must-Have Base Module Installer
# Reads modules from YAML manifest and installs them via Odoo CLI
# Usage: ./scripts/odoo_install_oca_must_have.sh [manifest_path]

MANIFEST="${1:-config/oca/oca_must_have_base.yml}"

: "${ODOO_BIN:=odoo}"
: "${ODOO_DB:?Set ODOO_DB}"
: "${ODOO_ADMIN_PASS:?Set ODOO_ADMIN_PASS}"
: "${ODOO_ADDONS_PATH:?Set ODOO_ADDONS_PATH (comma-separated)}"

# Extract modules from YAML manifest
MODULES="$(python3 -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(",".join(d["modules"]))' "$MANIFEST")"

echo "[oca] installing modules from: $MANIFEST"
echo "[oca] modules: ${MODULES}"

# Install/upgrade in one pass; --stop-after-init makes it CI-friendly
$ODOO_BIN \
  -d "$ODOO_DB" \
  --addons-path "$ODOO_ADDONS_PATH" \
  --without-demo=all \
  -i "$MODULES" \
  --stop-after-init \
  --log-level=info \
  --admin-passwd "$ODOO_ADMIN_PASS"

echo "[oca] install OK"
