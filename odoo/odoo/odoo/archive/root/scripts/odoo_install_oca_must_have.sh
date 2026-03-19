#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# OCA Must-Have Module Installer (Odoo 19 CE)
# =============================================================================
# Reads config/oca/module_allowlist.yml (all packs) or a single manifest,
# validates modules against docs/oca/ADDON_NAMES.txt inventory, and installs.
#
# Usage:
#   ./scripts/odoo_install_oca_must_have.sh                          # all packs
#   ./scripts/odoo_install_oca_must_have.sh config/oca/oca_must_have_base.yml  # single manifest
#   ./scripts/odoo_install_oca_must_have.sh --dry-run                # print only
#   ./scripts/odoo_install_oca_must_have.sh --pack accounting_core   # single pack
#
# Environment:
#   ODOO_BIN         — odoo binary (default: odoo)
#   ODOO_DB          — database name (required)
#   ODOO_ADMIN_PASS  — admin password (required unless --dry-run)
#   ODOO_ADDONS_PATH — comma-separated addons path (required unless --dry-run)
# =============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLOWLIST="$ROOT/config/oca/module_allowlist.yml"
INVENTORY="$ROOT/docs/oca/ADDON_NAMES.txt"

DRY_RUN=false
PACK_FILTER=""
MANIFEST=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --pack) PACK_FILTER="$2"; shift 2 ;;
    *.yml|*.yaml) MANIFEST="$1"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Single manifest mode (legacy)
if [[ -n "$MANIFEST" ]]; then
  MODULES="$(python3 -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(",".join(d["modules"]))' "$MANIFEST")"
  echo "[oca] installing modules from: $MANIFEST"
  echo "[oca] modules: ${MODULES}"
  MODULE_COUNT=$(echo "$MODULES" | tr ',' '\n' | wc -l)
else
  # Allowlist mode: read all packs in install order, filter by inventory
  MODULES=$(python3 - "$ALLOWLIST" "$INVENTORY" "$PACK_FILTER" <<'PY'
import sys, yaml, pathlib

allowlist_path, inventory_path = sys.argv[1], sys.argv[2]
pack_filter = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ""

with open(allowlist_path) as f:
    config = yaml.safe_load(f)

inventory = set()
inv_path = pathlib.Path(inventory_path)
if inv_path.exists():
    inventory = set(inv_path.read_text().strip().split("\n"))

modules, skipped = [], []
for pack_name in config.get("install_order", []):
    if pack_filter and pack_name != pack_filter:
        continue
    for m in config.get("packs", {}).get(pack_name, []):
        if not inventory or m in inventory:
            modules.append(m)
        else:
            skipped.append(m)

if skipped:
    print(f"# Skipped (not in 19.0 inventory): {', '.join(skipped)}", file=sys.stderr)

print(",".join(modules))
PY
  )
  MODULE_COUNT=$(echo "$MODULES" | tr ',' '\n' | wc -l)
  echo "[oca] source: module_allowlist.yml (all packs)"
  if [[ -n "$PACK_FILTER" ]]; then
    echo "[oca] pack filter: $PACK_FILTER"
  fi
  echo "[oca] installable modules: $MODULE_COUNT"
fi

if [[ -z "$MODULES" || "$MODULES" == "#"* ]]; then
  echo "[oca] ERROR: No installable modules found"
  exit 1
fi

if $DRY_RUN; then
  echo "[oca] dry-run module list:"
  echo "$MODULES" | tr ',' '\n' | nl
  exit 0
fi

: "${ODOO_BIN:=odoo}"
: "${ODOO_DB:?Set ODOO_DB}"
: "${ODOO_ADMIN_PASS:?Set ODOO_ADMIN_PASS}"
: "${ODOO_ADDONS_PATH:?Set ODOO_ADDONS_PATH (comma-separated)}"

echo "[oca] installing $MODULE_COUNT modules into db=$ODOO_DB ..."

$ODOO_BIN \
  -d "$ODOO_DB" \
  --addons-path "$ODOO_ADDONS_PATH" \
  --without-demo=all \
  -i "$MODULES" \
  --stop-after-init \
  --log-level=warn \
  --admin-passwd "$ODOO_ADMIN_PASS"

echo "[oca] install OK — $MODULE_COUNT modules installed"
