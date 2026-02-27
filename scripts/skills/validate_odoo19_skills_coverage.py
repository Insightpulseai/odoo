#!/usr/bin/env python3
"""
validate_odoo19_skills_coverage.py

Validates that the repository contains all skill stub directories required by
the coverage SSOT (ssot/skills/odoo19_docs_coverage.yaml).

Exits:
  0 — all expected stubs present
  1 — one or more stubs missing

Output (stdout): JSON with structured coverage broken down by section:
  {
    "coverage": {
      "odoo19_docs":         { "total": N, "found": N, "missing": N, "pct": 100.0 },
      "vercel_agent_skills": { "total": N, "found": N, "missing": N, "pct": 100.0 },
      "supabase_agent_skills": { ... }
    },
    "overall": { "total": N, "found": N, "missing": N, "pct": 100.0 },
    "missing_skills": []
  }
"""

import sys
import json
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
SSOT_PATH = REPO_ROOT / "ssot" / "skills" / "odoo19_docs_coverage.yaml"
SKILLS_DIR = REPO_ROOT / "skills"

# Groups that belong to external skill packs (not Odoo docs)
EXTERNAL_PACK_GROUPS = {"vercel_agent_skills", "supabase_agent_skills"}


def check_group(group: str, apps: dict) -> dict:
    total, found, missing = 0, 0, []
    for _app, paths in apps.items():
        for p in paths:
            total += 1
            if (SKILLS_DIR / p).is_dir():
                found += 1
            else:
                missing.append(p)
    pct = round(found / total * 100, 2) if total > 0 else 100.0
    return {"total": total, "found": found, "missing": len(missing), "pct": pct,
            "_missing_paths": missing}


def main():
    if not SSOT_PATH.exists():
        print(f"Error: SSOT file not found at {SSOT_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(SSOT_PATH) as f:
        ssot = yaml.safe_load(f)

    expected = ssot.get("expected", {})

    # Split into odoo19_docs vs external skill packs
    odoo_groups = {g: a for g, a in expected.items() if g not in EXTERNAL_PACK_GROUPS}
    ext_groups   = {g: a for g, a in expected.items() if g in EXTERNAL_PACK_GROUPS}

    coverage: dict = {}

    # --- Odoo 19 docs coverage (aggregated) ---
    odoo_total, odoo_found, odoo_missing = 0, 0, []
    for group, apps in odoo_groups.items():
        r = check_group(group, apps)
        odoo_total += r["total"]
        odoo_found += r["found"]
        odoo_missing.extend(r["_missing_paths"])
    odoo_pct = round(odoo_found / odoo_total * 100, 2) if odoo_total > 0 else 100.0
    coverage["odoo19_docs"] = {
        "total": odoo_total, "found": odoo_found,
        "missing": len(odoo_missing), "pct": odoo_pct,
    }

    # --- External skill packs (one section each) ---
    all_ext_missing: list = []
    for group, apps in ext_groups.items():
        r = check_group(group, apps)
        coverage[group] = {
            "total": r["total"], "found": r["found"],
            "missing": r["missing"], "pct": r["pct"],
        }
        all_ext_missing.extend(r["_missing_paths"])

    # --- Overall ---
    all_missing = odoo_missing + all_ext_missing
    all_total   = sum(v["total"] for v in coverage.values())
    all_found   = sum(v["found"] for v in coverage.values())
    overall_pct = round(all_found / all_total * 100, 2) if all_total > 0 else 100.0

    output = {
        "coverage": coverage,
        "overall": {"total": all_total, "found": all_found,
                    "missing": len(all_missing), "pct": overall_pct},
        "missing_skills": all_missing,
    }

    print(json.dumps(output, indent=2))

    if all_missing:
        print(
            "\n[FAIL] Missing skill stubs. Create stub directories for each entry in missing_skills.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("\n[OK] All expected skill stubs are present.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
