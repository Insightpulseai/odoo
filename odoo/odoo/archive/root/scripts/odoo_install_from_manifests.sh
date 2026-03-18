#!/usr/bin/env bash
set -euo pipefail

# OCA Multi-Manifest Module Installer
# Reads modules from one or more YAML manifests (with include support) and installs them
# Usage: ./scripts/odoo_install_from_manifests.sh <manifest.yml> [manifest2.yml ...]

: "${ODOO_BIN:=odoo}"
: "${ODOO_DB:?Set ODOO_DB}"
: "${ODOO_ADMIN_PASS:?Set ODOO_ADMIN_PASS}"
: "${ODOO_ADDONS_PATH:?Set ODOO_ADDONS_PATH (comma-separated)}"

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <manifest.yml> [manifest2.yml ...]" >&2
  exit 2
fi

# Extract and merge modules from all manifests (supports includes)
MODULES="$(python3 - "$@" <<'PY'
import sys
import yaml
from pathlib import Path

def load(p: Path):
    with p.open("r") as f:
        return yaml.safe_load(f) or {}

def resolve_manifest(p: Path, seen=None):
    if seen is None:
        seen = set()
    p = p.resolve()
    if p in seen:
        return []
    seen.add(p)

    d = load(p)
    mods = list(d.get("modules") or [])

    # Process includes relative to manifest directory
    for inc in (d.get("includes") or []):
        inc_path = (p.parent / inc).resolve()
        if inc_path.exists():
            mods += resolve_manifest(inc_path, seen)

    # de-dupe preserving order
    out = []
    s = set()
    for m in mods:
        if m and m not in s:
            s.add(m)
            out.append(m)
    return out

mods = []
s = set()
for arg in sys.argv[1:]:
    for m in resolve_manifest(Path(arg)):
        if m not in s:
            s.add(m)
            mods.append(m)

if not mods:
    raise SystemExit("No modules resolved from manifests")

print(",".join(mods))
PY
)"

echo "[oca] installing from manifests: $*"
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
