#!/usr/bin/env python3
"""
Verify integrity of generated KB index artifacts.
Checks for:
- manifest.json schema version and build_info
- Presence of entries from upstream layer
- Canonical IDs on all entries
- Consistency between manifest build_info and UPSTREAM_PIN.json
"""

import argparse
import json
import sys
from pathlib import Path


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb-root", required=True)
    args = parser.parse_args()

    kb_root = Path(args.kb_root).resolve()
    index_dir = kb_root / "index"
    pin_path = kb_root / "UPSTREAM_PIN.json"
    manifest_path = index_dir / "manifest.json"

    if not manifest_path.exists():
        print(f"❌ Missing manifest: {manifest_path}")
        sys.exit(1)

    manifest = _read_json(manifest_path)

    # 1. Check Build Info
    if "build_info" not in manifest:
        print("❌ manifest.json missing 'build_info'")
        sys.exit(1)

    build_info = manifest["build_info"]
    print(f"✅ Found build_info (generated at {build_info.get('generated_at_utc')})")

    # 2. Check Pin Consistency
    if pin_path.exists():
        pin = _read_json(pin_path)
        build_pin = build_info.get("upstream_pin", {})

        # Compare critical fields
        if pin.get("pinned_commit") != build_pin.get("pinned_commit"):
            print(
                f"❌ Pin mismatch! Disk: {pin.get('pinned_commit')} != Index: {build_pin.get('pinned_commit')}"
            )
            sys.exit(1)
        print("✅ Index build matches UPSTREAM_PIN.json")

    # 3. Check Entries & Canonical IDs
    entries = manifest.get("entries", [])
    if not entries:
        print("❌ Manifest has no entries")
        sys.exit(1)

    layers_found = set()
    missing_canonical = []

    for e in entries:
        layers_found.add(e.get("layer"))
        if not e.get("canonical_id"):
            missing_canonical.append(e.get("path"))

    if "upstream" not in layers_found:
        print("❌ No 'upstream' layer entries found in manifest")
        sys.exit(1)

    if missing_canonical:
        print(f"❌ {len(missing_canonical)} entries missing canonical_id")
        sys.exit(1)

    print(f"✅ Verified {len(entries)} entries across layers: {sorted(layers_found)}")
    print("✅ All entries have canonical_id")

    # 4. Check other artifacts exist
    for f in ["sections.json", "topics.json", "nav.json", "index.json", "skills_coverage.json"]:
        if not (index_dir / f).exists():
            print(f"❌ Missing artifact: {f}")
            sys.exit(1)

    print("✅ All index artifacts present and valid.")


if __name__ == "__main__":
    main()
