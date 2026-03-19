#!/usr/bin/env bash
# =============================================================================
# install-oca-modules.sh — SSOT-driven OCA module installation
#
# Thin wrapper around install_oca_from_ssot.py.
# Reads: ssot/odoo/oca_repos.yaml, ssot/odoo/oca_lock.yaml
# Requires: python3, pyyaml
#
# Usage:
#   ./scripts/odoo/install-oca-modules.sh [--dry-run] [--json] [--strict]
#
# Legacy category-based installation is no longer supported.
# For the old behavior, see scripts/odoo/_legacy_install_oca.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$SCRIPT_DIR/install_oca_from_ssot.py" "$@"
