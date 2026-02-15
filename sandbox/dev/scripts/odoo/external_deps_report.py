#!/usr/bin/env python3
import ast
import json
import os
import sys
from pathlib import Path

"""
Scans addons_path roots for __manifest__.py and reports external_dependencies:
  - python (pip)
  - bin (apt / system)

Usage:
  python scripts/odoo/external_deps_report.py /mnt/extra-addons > deps.json
"""

def read_manifest(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    # manifests are python dict literals; ast.literal_eval is usually enough
    try:
        return ast.literal_eval(txt)
    except Exception:
        # fallback: execute-like parse is risky; just skip if not literal-evalable
        return {}

def main() -> int:
    if len(sys.argv) < 2:
        print("missing addons root(s)", file=sys.stderr)
        return 2
    roots = [Path(p) for p in sys.argv[1:]]

    py = {}
    bin_ = {}
    for root in roots:
        if not root.exists():
            continue
        for manifest in root.rglob("__manifest__.py"):
            mod = manifest.parent.name
            data = read_manifest(manifest)
            ext = data.get("external_dependencies") or {}
            if "python" in ext:
                py[mod] = sorted(set(ext.get("python") or []))
            if "bin" in ext:
                bin_[mod] = sorted(set(ext.get("bin") or []))

    report = {"python": py, "bin": bin_}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
