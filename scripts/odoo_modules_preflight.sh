#!/usr/bin/env bash
# =============================================================================
# Preflight: validate that every module in an install set file exists
# in one of the known addons paths.
#
# Usage (inside container):
#   ./scripts/odoo_modules_preflight.sh config/install_sets/ppm_parity_autogen.txt
#
# Usage (host, with overrides):
#   ADDONS_PATHS="vendor/oca vendor/oca/OCA external-src addons/ipai addons" \
#       ./scripts/odoo_modules_preflight.sh config/install_sets/ppm_parity_autogen.txt
# =============================================================================
set -euo pipefail

SET_FILE="${1:?Usage: $0 <set_file.txt>}"

if [[ ! -f "$SET_FILE" ]]; then
    echo "ERROR: set file not found: $SET_FILE" >&2
    exit 1
fi

# Default: container paths. Override with ADDONS_PATHS env var.
DEFAULT_PATHS="/usr/lib/python3/dist-packages/odoo/addons /mnt/extra-addons/oca /mnt/extra-addons/ipai /mnt/extra-addons"
ADDONS_PATHS="${ADDONS_PATHS:-$DEFAULT_PATHS}"

missing=0
core=0
found=0

while IFS= read -r mod; do
    [[ "$mod" =~ ^\s*# ]] && continue
    [[ -z "${mod// /}" ]] && continue

    mod_found=0
    for p in $ADDONS_PATHS; do
        # Check direct path
        if [[ -d "$p/$mod" ]] && [[ -f "$p/$mod/__manifest__.py" || -f "$p/$mod/__openerp__.py" ]]; then
            mod_found=1
            break
        fi
        # Check one level deeper (OCA repo structure: path/repo/module)
        for subdir in "$p"/*/; do
            if [[ -d "${subdir}${mod}" ]] && [[ -f "${subdir}${mod}/__manifest__.py" || -f "${subdir}${mod}/__openerp__.py" ]]; then
                mod_found=1
                break 2
            fi
        done
    done

    if [[ $mod_found -eq 1 ]]; then
        found=$((found + 1))
    else
        echo "CORE/UNKNOWN: $mod"
        core=$((core + 1))
    fi
done < "$SET_FILE"

echo ""
echo "================================================================================"
echo "Preflight: $SET_FILE"
echo "  Found in addons: $found"
echo "  Core/unknown:    $core"
echo "================================================================================"

if [[ $missing -gt 0 ]]; then
    echo "ERROR: $missing modules missing from all addons paths"
    exit 2
fi

echo "OK: preflight passed"
