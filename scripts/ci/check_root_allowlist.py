#!/usr/bin/env python3
"""Check that root directory complies with allowlist."""

import json
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).parent.parent.parent
    allowlist_file = repo_root / ".insightpulse" / "repo-root-allowlist.json"

    if not allowlist_file.exists():
        print(f"❌ ERROR: Missing allowlist file: {allowlist_file}")
        sys.exit(1)

    # Load allowlist
    with open(allowlist_file) as f:
        allowlist = json.load(f)

    allowed_files = set(allowlist["allow_root_files"])
    allowed_dirs = set(allowlist["allow_root_dirs"])

    # Get actual root items
    actual_files = [
        f.name for f in repo_root.iterdir() if f.is_file() and not f.name.startswith(".git")
    ]
    actual_hidden_files = [
        f.name
        for f in repo_root.iterdir()
        if f.is_file() and f.name.startswith(".") and not f.name.startswith(".git")
    ]
    actual_dirs = [
        d.name for d in repo_root.iterdir() if d.is_dir() and d.name not in (".", "..")
    ]

    all_actual_files = actual_files + actual_hidden_files
    all_actual_dirs = actual_dirs

    # Check for violations
    violations_files = [f for f in all_actual_files if f not in allowed_files]
    violations_dirs = [d for d in all_actual_dirs if d not in allowed_dirs]

    if violations_files or violations_dirs:
        print("❌ Root directory violations found!\n")

        if violations_files:
            print("📄 Disallowed files at root:")
            for f in sorted(violations_files):
                print(f"  - {f}")
            print()

        if violations_dirs:
            print("📁 Disallowed directories at root:")
            for d in sorted(violations_dirs):
                print(f"  - {d}")
            print()

        print("📋 How to fix:")
        print("  1. Move files to appropriate directories:")
        print("     - Documentation (*.md): docs/")
        print("     - Scripts (*.sh, *.py): scripts/")
        print("     - Data files (*.csv, *.json): artifacts/ or docs/evidence/")
        print("     - Out-of-scope code: archive/root/ (with migration plan)")
        print()
        print("  2. If the file/dir is truly needed at root:")
        print("     - Add it to .insightpulse/repo-root-allowlist.json")
        print("     - Justify in PR description why it must be at root")
        print()
        print("  3. See docs/policy/ODOO_REPO_SCOPE.md for guidance")

        sys.exit(1)
    else:
        print("✅ Root directory complies with allowlist")
        print(f"   Files: {len(all_actual_files)} allowed")
        print(f"   Dirs: {len(all_actual_dirs)} allowed")


if __name__ == "__main__":
    main()
