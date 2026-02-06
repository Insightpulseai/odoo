#!/usr/bin/env bash
set -euo pipefail

# Finds ipai_* addons and validates:
# 1) manifest exists
# 2) all referenced data files exist
# 3) python compiles
# 4) xml is well-formed
#
# Optional: can also run an Odoo install test if ODOO_BIN/DB available.

ADDONS_ROOT="${ADDONS_ROOT:-addons}"
FAIL=0

mods=$(find "$ADDONS_ROOT" -maxdepth 4 -type f -name "__manifest__.py" -path "*/ipai_*/*" | sort || true)
if [[ -z "${mods:-}" ]]; then
  echo "No ipai_* manifests found under $ADDONS_ROOT"
  exit 0
fi

python - <<'PY'
import ast, sys, pathlib, xml.etree.ElementTree as ET
from typing import List

root = pathlib.Path("${ADDONS_ROOT}")
manifests = sorted(root.rglob("ipai_*/__manifest__.py"))

fail = 0
for m in manifests:
    moddir = m.parent
    try:
        data = ast.literal_eval(m.read_text())
    except Exception as e:
        print(f"[FAIL] {moddir}: invalid __manifest__.py: {e}")
        fail += 1
        continue

    # Check referenced files exist
    missing: List[str] = []
    for rel in data.get("data", []):
        p = moddir / rel
        if not p.exists():
            missing.append(str(p))
    if missing:
        print(f"[FAIL] {moddir}: missing manifest data files:")
        for x in missing: print("  -", x)
        fail += 1
        continue

    # Compile py
    try:
        for py in moddir.rglob("*.py"):
            compile(py.read_text(), str(py), "exec")
    except Exception as e:
        print(f"[FAIL] {moddir}: python compile error: {e}")
        fail += 1
        continue

    # Parse xml
    try:
        for xml in moddir.rglob("*.xml"):
            ET.parse(xml)
    except Exception as e:
        print(f"[FAIL] {moddir}: xml parse error in {xml}: {e}")
        fail += 1
        continue

    print(f"[OK] {moddir.name}")

sys.exit(1 if fail else 0)
PY