#!/usr/bin/env python3
"""
Generate addons_path for Odoo configuration.

Odoo does NOT support globs in addons_path (e.g., addons/OCA/* won't work).
This script generates the deterministic comma-separated list of addon paths.

Usage:
    python3 scripts/gen_addons_path.py

    # Set as environment variable
    export ADDONS_PATH="$(python3 scripts/gen_addons_path.py)"

    # Use with Odoo
    ./odoo-bin -c config/odoo.conf --addons-path="$ADDONS_PATH"
"""

import os
import glob
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_addons_paths():
    """Generate ordered list of addon paths."""
    paths = []

    # 1. Custom addons (ipai_* and other custom modules)
    custom_addons = os.path.join(ROOT, "addons")
    if os.path.isdir(custom_addons):
        paths.append(custom_addons)

    # 2. IPAI modules (explicit path for clarity)
    ipai_addons = os.path.join(ROOT, "addons", "ipai")
    if os.path.isdir(ipai_addons):
        paths.append(ipai_addons)

    # 3. OCA modules (each repo is a separate path)
    oca_root = os.path.join(ROOT, "addons", "OCA")
    if os.path.isdir(oca_root):
        # Sort for deterministic order
        for repo in sorted(glob.glob(os.path.join(oca_root, "*"))):
            if os.path.isdir(repo):
                # Check if it's an actual addon repo (has __manifest__.py files inside)
                has_addons = any(
                    os.path.exists(os.path.join(repo, d, "__manifest__.py"))
                    for d in os.listdir(repo)
                    if os.path.isdir(os.path.join(repo, d))
                )
                if has_addons or os.path.islink(repo):
                    paths.append(repo)

    # 4. External sources (if cloned separately)
    external_root = os.path.join(ROOT, "external-src")
    if os.path.isdir(external_root):
        for repo in sorted(glob.glob(os.path.join(external_root, "*"))):
            if os.path.isdir(repo):
                has_addons = any(
                    os.path.exists(os.path.join(repo, d, "__manifest__.py"))
                    for d in os.listdir(repo)
                    if os.path.isdir(os.path.join(repo, d))
                )
                if has_addons:
                    paths.append(repo)

    return paths


def main():
    """Main entry point."""
    paths = get_addons_paths()

    if "--verbose" in sys.argv or "-v" in sys.argv:
        print("# Generated addons_path entries:", file=sys.stderr)
        for i, path in enumerate(paths, 1):
            print(f"#   {i}. {path}", file=sys.stderr)
        print(f"# Total: {len(paths)} paths", file=sys.stderr)
        print("", file=sys.stderr)

    print(",".join(paths))


if __name__ == "__main__":
    main()
