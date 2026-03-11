#!/usr/bin/env python3
"""
Build OCA Parity Bundle
Generates an install manifest from the EE parity mapping, extracting all OCA modules.
Usage: ./scripts/odoo_parity/build_oca_bundle.py [mapping.yml] [output.yml]
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def load(p: Path):
    with p.open("r") as f:
        return yaml.safe_load(f) or {}


def dump(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        yaml.safe_dump(obj, f, sort_keys=False, default_flow_style=False)


def main():
    mapping_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config/ee_parity/ee_parity_mapping.yml")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("config/ee_parity/oca_parity_bundle.yml")

    if not mapping_path.exists():
        print(f"ERROR: mapping file not found: {mapping_path}", file=sys.stderr)
        return 2

    m = load(mapping_path)
    entries = m.get("mapping") or []

    # Extract OCA modules from all oca/ce strategy entries
    mods = []
    seen = set()
    for e in entries:
        if not isinstance(e, dict):
            continue
        strategy = e.get("strategy", "")
        # Include both OCA and CE modules for installation
        for mod in (e.get("oca_modules") or []):
            if mod and mod not in seen:
                seen.add(mod)
                mods.append(mod)
        if strategy == "ce":
            for mod in (e.get("ce_modules") or []):
                if mod and mod not in seen:
                    seen.add(mod)
                    mods.append(mod)

    # Build output manifest
    bundle = {
        "meta": {
            "odoo_version": "19.0",
            "purpose": "OCA modules for EE parity replacements",
            "generated": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_mapping": str(mapping_path),
        },
        "modules": mods,
        "policy": {
            "require_all_modules_installed": True,
            "fail_if_module_not_found": True,
        },
    }

    dump(out_path, bundle)

    print(f"OK: wrote {out_path} with {len(mods)} modules")
    print("Modules:")
    for m in mods:
        print(f"  - {m}")
    return 0


if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
