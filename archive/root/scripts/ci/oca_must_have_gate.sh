#!/usr/bin/env bash
set -euo pipefail

# OCA Must-Have Base Gate - CI Script
# Installs and verifies OCA must-have modules
# Usage: ./scripts/ci/oca_must_have_gate.sh
#
# Required environment variables:
#   ODOO_DB           - Database name
#   ODOO_ADMIN_PASS   - Admin password
#   ODOO_ADDONS_PATH  - Comma-separated addons paths
#
# Optional:
#   ODOO_BIN          - Odoo binary (default: odoo)
#   ODOO_PGURL        - Direct PostgreSQL URL for verification

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MANIFEST="${1:-config/oca/oca_must_have_base.yml}"
MANIFEST_PATH="$REPO_ROOT/$MANIFEST"

echo "========================================"
echo "  OCA Must-Have Base Gate"
echo "========================================"
echo ""

# Validate manifest exists
if [ ! -f "$MANIFEST_PATH" ]; then
    echo "ERROR: Manifest not found: $MANIFEST_PATH"
    exit 2
fi

# Check if this is a dry-run (no ODOO_DB set)
if [ -z "${ODOO_DB:-}" ] || [ -z "${ODOO_ADMIN_PASS:-}" ] || [ -z "${ODOO_ADDONS_PATH:-}" ]; then
    echo "[oca] Missing required environment variables."
    echo "[oca] Required: ODOO_DB, ODOO_ADMIN_PASS, ODOO_ADDONS_PATH"
    echo "[oca] Skipping OCA must-have gate (dry-run mode)"
    echo ""
    echo "To run with actual Odoo instance:"
    echo "  export ODOO_DB=odoo"
    echo "  export ODOO_ADMIN_PASS=admin"
    echo "  export ODOO_ADDONS_PATH=/opt/odoo/addons,/opt/odoo/oca-addons"
    echo "  ./scripts/ci/oca_must_have_gate.sh"
    exit 0
fi

echo "[oca] Manifest: $MANIFEST"
echo "[oca] Database: $ODOO_DB"
echo "[oca] Addons Path: $ODOO_ADDONS_PATH"
echo ""

# Step 1: Install modules
echo "[1/2] Installing OCA must-have modules..."
"$REPO_ROOT/scripts/odoo_install_oca_must_have.sh" "$MANIFEST"

# Step 2: Verify installation
echo ""
echo "[2/2] Verifying OCA must-have modules..."
"$REPO_ROOT/scripts/odoo_verify_oca_must_have.py" "$MANIFEST_PATH"

echo ""
echo "========================================"
echo "  OCA Must-Have Gate: PASSED"
echo "========================================"
