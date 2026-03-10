#!/usr/bin/env bash
# gate_modules.sh - Run deterministic module gate before deployment
#
# Usage:
#   ODOO_MODULES=ipai_workos_core,ipai_finance_ppm ./scripts/ci_gate/gate_modules.sh
#
# Environment Variables:
#   ODOO_MODULES - Comma-separated list of modules to gate (required)
#   SKIP_VIEW_CHECK - Set to 1 to skip Odoo 18 view convention check

set -euo pipefail

MODS="${ODOO_MODULES:?Set ODOO_MODULES='a,b,c'}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running module gate for: $MODS"
echo ""

# Get all addons roots
mapfile -t ROOTS < <("$SCRIPT_DIR/compute_addons_roots.sh")

# Build arguments
ARGS=()
for r in "${ROOTS[@]}"; do
  ARGS+=(--addons-root "$r")
done

# Add skip view check if requested
if [ "${SKIP_VIEW_CHECK:-0}" = "1" ]; then
  ARGS+=(--skip-view-check)
fi

# Run the gate
python3 "$SCRIPT_DIR/module_gate.py" "${ARGS[@]}" --modules "$MODS"
