#!/usr/bin/env bash
# Smoke Test: Verify Odoo can be imported as Python package
# Usage: ./scripts/smoke_import_odoo.sh

set -euo pipefail

echo "🔍 Smoke Test: Odoo Python Import"
echo "===================================="

# Check if Odoo is available via pip/editable install
if python3 -c "import odoo; print(f'Odoo version: {odoo.release.version}')" 2>/dev/null; then
    echo "✅ PASS: Odoo successfully imported"
    exit 0
else
    echo "❌ FAIL: Cannot import Odoo as Python package"
    echo ""
    echo "Expected: Odoo installed via pip or editable install"
    echo "Actual: Import failed"
    exit 1
fi
