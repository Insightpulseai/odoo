#!/usr/bin/env python3
"""
generate_addons_path.py

Generate an Odoo addons_path fragment for all aggregated OCA repos.
Assumes OCA repos live under ./addons/oca/<repo>.

Usage:
    python3 scripts/oca/generate_addons_path.py

Output: comma-separated list of absolute paths to OCA repo directories.
"""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    oca_dir = repo_root / "addons" / "oca"

    if not oca_dir.exists():
        print("")  # Empty output if oca dir doesn't exist
        return

    # Find all OCA repo directories (ignore dotfiles and non-directories)
    repos = sorted([p for p in oca_dir.iterdir() if p.is_dir() and not p.name.startswith(".")])

    if not repos:
        print("")
        return

    # IMPORTANT: Odoo does not recurse directories for addons discovery.
    # You must list each repo directory explicitly.
    print(",".join(str(p) for p in repos))


if __name__ == "__main__":
    main()
