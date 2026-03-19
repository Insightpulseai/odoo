#!/usr/bin/env python3
"""
Check for Undocumented Specs
Identifies spec bundles that are not indexed or referenced in docs
"""

import sys
from pathlib import Path


def main():
    """Check for spec bundles not documented in repo index"""
    repo_root = Path(__file__).parent.parent
    spec_dir = repo_root / "spec"
    index_file = repo_root / "docs" / "INDEX.md"

    # Find all spec bundles
    spec_bundles = [
        d.name
        for d in spec_dir.iterdir()
        if d.is_dir() and (d / "constitution.md").exists()
    ]

    if not spec_bundles:
        print("No spec bundles found")
        sys.exit(0)

    # Check if index exists
    if not index_file.exists():
        print(f"WARNING: docs/INDEX.md not found. Run generate_repo_index.py first.")
        print(f"Found {len(spec_bundles)} spec bundles that should be indexed.")
        sys.exit(0)

    # Read index
    index_content = index_file.read_text(encoding="utf-8")

    # Check each bundle is referenced
    undocumented = []
    for bundle in spec_bundles:
        if bundle not in index_content:
            undocumented.append(bundle)

    if undocumented:
        print(f"Found {len(undocumented)} undocumented spec bundle(s):")
        for bundle in undocumented:
            print(f"  - {bundle}")
        print()
        print("These bundles should be added to docs/INDEX.md")
        sys.exit(1)
    else:
        print(f"✓ All {len(spec_bundles)} spec bundles are documented in INDEX.md")
        sys.exit(0)


if __name__ == "__main__":
    main()
