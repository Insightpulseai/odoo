#!/usr/bin/env bash
# ===========================================================================
# generate_addons_path.sh — Enumerate OCA repos and emit complete addons_path
# ===========================================================================
# Odoo does NOT recurse into subdirectories when scanning addons_path.
# Each OCA repo root (containing module dirs with __manifest__.py) must be
# listed as a separate comma-separated entry.
#
# Usage:
#   ./scripts/odoo/generate_addons_path.sh                          # devcontainer default
#   ./scripts/odoo/generate_addons_path.sh /workspaces/odoo         # explicit prefix
#   ./scripts/odoo/generate_addons_path.sh /path/to/odoo --inject   # write into odoo.conf
#
# Options:
#   --inject   Also update the addons_path line in $PREFIX/config/dev/odoo.conf
#              and $PREFIX/.devcontainer/odoo.devcontainer.conf
#   --core PATH  Override core addons path (default: /usr/lib/python3/dist-packages/odoo/addons)
# ===========================================================================
set -euo pipefail

PREFIX="/workspaces/odoo"
INJECT=false
CORE="/usr/lib/python3/dist-packages/odoo/addons"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --inject) INJECT=true; shift ;;
        --core)   CORE="$2"; shift 2 ;;
        *)        PREFIX="$1"; shift ;;
    esac
done

OCA_ROOT="${PREFIX}/addons/oca"

if [ ! -d "$OCA_ROOT" ]; then
    echo "ERROR: OCA root not found: $OCA_ROOT" >&2
    exit 1
fi

# Build path: core + each OCA repo with modules + ipai + local
paths="${CORE}"
repo_count=0
total_modules=0

for repo_dir in "${OCA_ROOT}"/*/; do
    [ -d "$repo_dir" ] || continue
    # Skip hidden dirs (.git, .DS_Store dirs, etc.)
    repo=$(basename "$repo_dir")
    [[ "$repo" == .* ]] && continue

    mod_count=$(find "$repo_dir" -maxdepth 2 -name "__manifest__.py" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$mod_count" -gt 0 ]; then
        paths="${paths},${repo_dir%/}"
        repo_count=$((repo_count + 1))
        total_modules=$((total_modules + mod_count))
        echo "  OCA: $repo ($mod_count modules)" >&2
    else
        echo "  SKIP: $repo (0 modules)" >&2
    fi
done

paths="${paths},${PREFIX}/addons/ipai,${PREFIX}/addons/local"

echo "Total: $repo_count repos, $total_modules modules" >&2
echo "$paths"

# Optionally inject into config files
if $INJECT; then
    for conf in "${PREFIX}/config/dev/odoo.conf" "${PREFIX}/.devcontainer/odoo.devcontainer.conf"; do
        if [ -f "$conf" ]; then
            sed -i.bak "s|^addons_path = .*|addons_path = ${paths}|" "$conf"
            rm -f "${conf}.bak"
            echo "INJECTED: $conf" >&2
        fi
    done
fi
