#!/usr/bin/env python3
"""Check file extension placement rules against taxonomy."""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PLACEMENT_RULES = {
    "docs": {
        "forbidden": {".py", ".ts", ".tsx", ".sql", ".tf", ".bicep"},
    },
    "ssot": {
        "forbidden": {".md", ".py", ".ts", ".tsx", ".sh"},
    },
}

SKIP_DIRS = {"archive", "node_modules", ".git", "__pycache__", ".venv"}


def check_placement(strict=False):
    violations = []

    for folder, rules in PLACEMENT_RULES.items():
        folder_path = REPO_ROOT / folder
        if not folder_path.exists():
            continue

        for f in folder_path.rglob("*"):
            if f.is_dir():
                continue
            # Skip archive and hidden dirs
            parts = f.relative_to(REPO_ROOT).parts
            if any(p in SKIP_DIRS for p in parts):
                continue

            suffix = f.suffix.lower()
            if suffix in rules["forbidden"]:
                rel = f.relative_to(REPO_ROOT)
                violations.append(f"{rel}: {suffix} not allowed in {folder}/")

    if violations:
        mode = "FAIL" if strict else "WARN"
        print(f"{mode}: {len(violations)} placement violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1 if strict else 0

    print("PASS: No placement violations")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Check file taxonomy placement rules")
    parser.add_argument("--strict", action="store_true", help="Fail on violations instead of warning")
    args = parser.parse_args()
    return check_placement(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
