#!/usr/bin/env bash
# =============================================================================
# Check for install set drift (local/agent use).
# Regenerates all sets from current addons state and fails if committed
# autogen files differ from freshly generated output.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Use repo paths (not container mounts)
export OCA_ROOTS="${OCA_ROOTS:-vendor/oca vendor/oca/OCA external-src}"
export CUSTOM_ROOT="${CUSTOM_ROOT:-addons/ipai addons}"

./scripts/regen_install_sets.sh

if ! git diff --exit-code -- config/install_sets; then
    echo ""
    echo "ERROR: install set drift detected."
    echo "Run './scripts/regen_install_sets.sh' and commit the changes."
    echo ""
    git --no-pager diff -- config/install_sets || true
    exit 2
fi

echo "OK: no install set drift"
