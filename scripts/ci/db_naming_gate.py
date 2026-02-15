#!/usr/bin/env python3
"""
Database Naming Enforcement Gate
=================================

Scans the repository for database name references and enforces the allowlist:
- odoo_dev
- odoo_staging
- odoo_prod

Scans:
- docker-compose*.yml files
- config/**/odoo.conf files
- .env* files (excluding .env.example)

Exit codes:
- 0: All database names comply with allowlist
- 1: Forbidden database names found
"""

import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Canonical database name allowlist
ALLOWED_DB_NAMES = {"odoo_dev", "odoo_stage", "odoo_prod"}

# File patterns to scan
SCAN_PATTERNS = [
    "docker-compose*.yml",
    "config/**/odoo.conf",
    ".env*",
]

# Exclude patterns
EXCLUDE_PATTERNS = [
    ".env.example",
    "**/.env.example",
    "**/node_modules/**",
    "archive/**",
    "**/archive/**",
    "templates/**",  # Template files may contain example DB names
    "infra/do-oca-stack/**",  # OCA reference stack (not canonical)
    "odoo/compose/**",  # Example/pattern stack (not canonical)
]


def find_db_references(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find database name references in a file.

    Returns list of (line_number, line_content, db_name) tuples.
    """
    results = []

    # Patterns to detect database names
    patterns = [
        r"database[:\s=]+['\"]?(\w+)['\"]?",  # database: odoo_dev, database=odoo_dev
        r"db_name[:\s=]+['\"]?(\w+)['\"]?",   # db_name = odoo_dev, db_name: odoo_dev
        r"POSTGRES_DB[:\s=]+['\"]?(\w+)['\"]?",  # POSTGRES_DB=odoo_dev
        r"ODOO_DB[:\s=]+['\"]?(\w+)['\"]?",   # ODOO_DB=odoo_dev
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                if line.strip().startswith('#') or line.strip().startswith(';'):
                    continue

                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        db_name = match.group(1)
                        # Only report if it looks like an Odoo database name
                        if db_name.startswith('odoo') or 'odoo' in db_name.lower():
                            results.append((line_num, line.strip(), db_name))
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    return results


def scan_repository(root_dir: Path) -> dict:
    """
    Scan repository for database name references.

    Returns dict mapping file paths to list of violations.
    """
    violations = {}

    for pattern in SCAN_PATTERNS:
        for file_path in root_dir.rglob(pattern):
            # Skip excluded paths
            rel_path = str(file_path.relative_to(root_dir))
            if any(rel_path.startswith(excl.rstrip('**/')) for excl in EXCLUDE_PATTERNS if not excl.startswith('**/')):
                continue
            if any(file_path.match(excl) for excl in EXCLUDE_PATTERNS if excl.startswith('**/')):
                continue

            # Skip if not a file
            if not file_path.is_file():
                continue

            refs = find_db_references(file_path)
            if refs:
                # Filter to only forbidden names
                forbidden = [
                    (line_num, line, db_name)
                    for line_num, line, db_name in refs
                    if db_name not in ALLOWED_DB_NAMES
                ]

                if forbidden:
                    violations[file_path] = forbidden

    return violations


def main():
    """Main entry point."""
    root = Path(__file__).parent.parent.parent
    print(f"Scanning repository: {root}")
    print(f"Allowed database names: {', '.join(sorted(ALLOWED_DB_NAMES))}")
    print()

    violations = scan_repository(root)

    if not violations:
        print("✅ All database names comply with allowlist.")
        return 0

    print("❌ Forbidden database names found:\n")

    for file_path, refs in sorted(violations.items()):
        rel_path = file_path.relative_to(root)
        print(f"  {rel_path}:")
        for line_num, line, db_name in refs:
            print(f"    Line {line_num}: {line}")
            print(f"      → Database name '{db_name}' is not in allowlist")
        print()

    print("Allowed database names:")
    for db_name in sorted(ALLOWED_DB_NAMES):
        print(f"  - {db_name}")
    print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
