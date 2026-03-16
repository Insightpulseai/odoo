#!/usr/bin/env python3
"""
Deterministic Odoo addon gate (OCA-style).
- Validates __manifest__.py parse + required keys
- Builds a local dependency graph for modules found in addons roots
- Fails fast if requested modules have missing deps (not present in repo)
- Ensures Odoo 18 view convention: <tree> must not exist (use <list>)

Usage:
  python3 scripts/ci_gate/module_gate.py --addons-root addons --modules a,b,c
"""
import argparse
import ast
import os
import sys
import pathlib
import re
from collections import defaultdict, deque

REQ_KEYS = {"name", "version", "depends", "license"}
TREE_RE = re.compile(r"<\s*tree(\s|>)")


def load_manifest(p: pathlib.Path):
    """Load and parse __manifest__.py file."""
    txt = p.read_text(encoding="utf-8", errors="ignore")
    try:
        node = ast.parse(txt)
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Dict):
                return ast.literal_eval(stmt.value)
        # typical: dict literal file
        return ast.literal_eval(txt)
    except Exception as e:
        raise RuntimeError(f"manifest parse failed: {p}: {e}")


def find_modules(addons_roots):
    """Find all modules in given addons roots."""
    mods = {}
    for root in addons_roots:
        rootp = pathlib.Path(root)
        if not rootp.exists():
            continue
        for d in rootp.iterdir():
            if not d.is_dir():
                continue
            mf = d / "__manifest__.py"
            if mf.exists():
                mods[d.name] = d
    return mods


def validate_views(mod_path: pathlib.Path):
    """Check for Odoo 18 view convention violations (<tree> should be <list>)."""
    bad = []
    for p in mod_path.rglob("*.xml"):
        if "/static/" in str(p).replace("\\", "/"):
            continue
        try:
            s = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if TREE_RE.search(s):
            bad.append(p)
    return bad


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic Odoo addon gate (OCA-style)"
    )
    ap.add_argument(
        "--addons-root",
        action="append",
        required=True,
        help="repeat for each addons root (e.g., addons, addons/OCA/server-tools)",
    )
    ap.add_argument(
        "--modules",
        required=True,
        help="comma-separated list of modules to gate",
    )
    ap.add_argument(
        "--skip-view-check",
        action="store_true",
        help="skip Odoo 18 view convention check",
    )
    args = ap.parse_args()

    targets = [m.strip() for m in args.modules.split(",") if m.strip()]
    mods = find_modules(args.addons_root)

    print("=" * 60)
    print("Odoo Module Gate (OCA-style)")
    print("=" * 60)
    print(f"Targets: {', '.join(targets)}")
    print(f"Addons roots: {len(args.addons_root)}")
    print(f"Total modules found: {len(mods)}")
    print()

    # Check if target modules exist
    missing_targets = [m for m in targets if m not in mods]
    if missing_targets:
        print("ERROR: requested modules not found in addons roots:")
        for m in missing_targets:
            print(f"  - {m}")
        sys.exit(2)

    manifests = {}
    deps = defaultdict(list)
    missing_keys = []

    # Validate manifests
    for name, path in mods.items():
        mf = path / "__manifest__.py"
        try:
            d = load_manifest(mf)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(3)

        manifests[name] = d
        for k in REQ_KEYS:
            if k not in d:
                missing_keys.append((name, k))

        dep_list = d.get("depends") or []
        if not isinstance(dep_list, list):
            print(f"ERROR: depends not a list in {name}")
            sys.exit(4)
        deps[name] = dep_list

    if missing_keys:
        print("ERROR: missing required manifest keys:")
        for m, k in missing_keys[:50]:
            print(f"  - {m}: missing '{k}'")
        sys.exit(5)

    # Compute dependency closure for targets
    closure = set()
    q = deque(targets)
    missing_deps = defaultdict(list)

    while q:
        m = q.popleft()
        if m in closure:
            continue
        closure.add(m)
        for d in deps.get(m, []):
            if d not in mods:
                # Allow base Odoo modules (they're not in repo)
                if not d.startswith("base") and d not in (
                    "base",
                    "web",
                    "mail",
                    "contacts",
                    "sale",
                    "purchase",
                    "account",
                    "stock",
                    "mrp",
                    "crm",
                    "hr",
                    "project",
                    "website",
                    "portal",
                    "bus",
                    "digest",
                    "auth_signup",
                    "auth_oauth",
                    "resource",
                    "calendar",
                    "product",
                    "uom",
                    "sale_management",
                    "purchase_stock",
                    "analytic",
                    "board",
                    "spreadsheet",
                    "spreadsheet_dashboard",
                    "fetchmail",
                    "iap",
                    "im_livechat",
                    "note",
                    "phone_validation",
                    "sms",
                    "utm",
                    "payment",
                ):
                    missing_deps[m].append(d)
            else:
                q.append(d)

    if missing_deps:
        print("ERROR: missing dependency modules (not present in repo):")
        for m, ds in missing_deps.items():
            print(f"  - {m} missing: {', '.join(ds)}")
        sys.exit(6)

    # Odoo 18 XML view convention check (tree->list)
    if not args.skip_view_check:
        bad_views = []
        for m in closure:
            if m in mods:
                bad_views.extend([(m, p) for p in validate_views(mods[m])])

        if bad_views:
            print(
                "ERROR: Odoo 18 view convention violated (<tree> found). Use <list> instead:"
            )
            for m, p in bad_views[:80]:
                print(f"  - {m}: {p}")
            sys.exit(7)

    print("-" * 60)
    print("RESULT: GATE PASSED")
    print("-" * 60)
    print(f"Targets: {', '.join(targets)}")
    print(f"Closure size: {len(closure)} modules")
    print()


if __name__ == "__main__":
    main()
