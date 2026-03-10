#!/usr/bin/env python3
"""
EE Parity Gate Check
Ensures all EE features are mapped, verifies module installation, and blocks
ipai_enterprise_bridge changes until full parity coverage is achieved.

Usage: ./scripts/odoo_parity/check_ee_parity.py
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def load(p: Path):
    with p.open("r") as f:
        return yaml.safe_load(f) or {}


def git_changed_paths(base_ref="origin/main"):
    """Get list of changed files from base ref to HEAD."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return []
    return [x for x in out.splitlines() if x.strip()]


def main():
    catalog_path = Path("config/ee_parity/ee_feature_catalog.yml")
    mapping_path = Path("config/ee_parity/ee_parity_mapping.yml")

    if not catalog_path.exists():
        print(f"ERROR: catalog not found: {catalog_path}", file=sys.stderr)
        return 2
    if not mapping_path.exists():
        print(f"ERROR: mapping not found: {mapping_path}", file=sys.stderr)
        return 2

    catalog = load(catalog_path)
    mapping_doc = load(mapping_path)

    # Build feature ID -> feature dict
    features = {
        f["id"]: f
        for f in (catalog.get("features") or [])
        if isinstance(f, dict) and f.get("id")
    }

    # Build feature_id -> mapping entry dict
    entries = mapping_doc.get("mapping") or []
    mapped = {
        e.get("feature_id"): e
        for e in entries
        if isinstance(e, dict) and e.get("feature_id")
    }

    errors = []

    # 1) Ensure every catalog feature has a mapping entry
    missing_map = [fid for fid in features.keys() if fid not in mapped]
    if missing_map:
        errors.append(f"Missing mapping entries for feature IDs: {missing_map}")

    # 2) Ensure no entry is left "unmapped"
    unmapped = [
        fid for fid, e in mapped.items() if (e.get("status") or "unmapped") == "unmapped"
    ]
    if unmapped:
        errors.append(f"Unmapped features remain: {unmapped}")

    # 3) If Odoo DB connection is available, verify modules are installed
    PGURL = os.getenv("ODOO_PGURL")
    DBNAME = os.getenv("ODOO_DB")
    conn = None

    if psycopg2 and (PGURL or DBNAME):
        try:
            if PGURL:
                conn = psycopg2.connect(PGURL)
            else:
                conn = psycopg2.connect(
                    dbname=DBNAME,
                    user=os.getenv("PGUSER", "odoo"),
                    password=os.getenv("PGPASSWORD", "odoo"),
                    host=os.getenv("PGHOST", "127.0.0.1"),
                    port=int(os.getenv("PGPORT", "5432")),
                )
        except Exception as e:
            print(f"[parity] DB connection failed (continuing without module check): {e}")
            conn = None

    if conn:
        # Collect all required modules from ce/oca strategies
        required_mods = []
        for fid, e in mapped.items():
            strategy = e.get("strategy", "")
            if strategy == "ce":
                required_mods.extend(e.get("ce_modules") or [])
            if strategy == "oca":
                required_mods.extend(e.get("oca_modules") or [])

        # de-dupe
        seen = set()
        mods = []
        for m in required_mods:
            if m and m not in seen:
                seen.add(m)
                mods.append(m)

        if mods:
            cur = conn.cursor()
            cur.execute(
                "SELECT name, state FROM ir_module_module WHERE name = ANY(%s)", (mods,)
            )
            states = {n: s for (n, s) in cur.fetchall()}
            conn.close()

            missing = [m for m in mods if m not in states]
            bad = [m for m, s in states.items() if s not in ("installed", "to upgrade")]

            if missing:
                errors.append(f"Missing in ir_module_module: {missing}")
            if bad:
                errors.append(
                    f"Not installed: {', '.join(f'{m}={states[m]}' for m in bad)}"
                )
    else:
        print("[parity] No DB connection; skipping module install verification")

    # 4) Block changes to ipai bridge until ALL features are verified
    base_ref = os.getenv("PARITY_BASE_REF", "origin/main")
    changed = git_changed_paths(base_ref)

    # Detect if ipai bridge or addons/ipai are being modified
    touched_bridge = any(
        p.startswith("addons/ipai_enterprise_bridge")
        or p.startswith("addons/ipai/ipai_enterprise_bridge")
        for p in changed
    )

    not_verified = [
        fid for fid, e in mapped.items() if (e.get("status") not in ("verified",))
    ]

    if touched_bridge and not_verified:
        errors.append(
            f"ipai_enterprise_bridge changes are BLOCKED until all features are verified. "
            f"Not verified: {not_verified}"
        )

    # Report results
    if errors:
        print("FAIL: EE parity gate failed.")
        for err in errors:
            print(f"  - {err}")
        return 1

    # Summary
    total = len(features)
    verified = sum(1 for e in mapped.values() if e.get("status") == "verified")
    planned = sum(1 for e in mapped.values() if e.get("status") == "planned")
    installed = sum(1 for e in mapped.values() if e.get("status") == "installed")

    print("OK: EE parity gate passed.")
    print(f"  Total features: {total}")
    print(f"  Verified: {verified}")
    print(f"  Installed: {installed}")
    print(f"  Planned: {planned}")
    print(f"  Coverage: {(verified / total * 100) if total else 0:.1f}%")
    return 0


if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
