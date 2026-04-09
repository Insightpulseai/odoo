#!/usr/bin/env python3
"""Lint: detect __init__.py imports for files that don't exist.

Usage:
    python scripts/ci/check_phantom_imports.py [addons_path ...]

Defaults to addons/ipai/ if no path given.
Exit 0 = clean, Exit 1 = phantom imports found.
"""

import re
import sys
from pathlib import Path

IMPORT_RE = re.compile(r"^from\s+\.\s+import\s+(\w+)", re.MULTILINE)


def check_dir(base: Path) -> list[str]:
    errors = []
    for init in base.rglob("__init__.py"):
        pkg_dir = init.parent
        text = init.read_text(encoding="utf-8")
        for match in IMPORT_RE.finditer(text):
            name = match.group(1)
            if not (pkg_dir / f"{name}.py").exists() and not (pkg_dir / name / "__init__.py").exists():
                rel = init.relative_to(base)
                errors.append(f"  {rel}: imports '{name}' but {name}.py does not exist")
    return errors


def main():
    paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else [Path("addons/ipai")]
    all_errors = []
    for p in paths:
        if not p.is_dir():
            print(f"SKIP: {p} is not a directory")
            continue
        all_errors.extend(check_dir(p))

    if all_errors:
        print(f"FAIL: {len(all_errors)} phantom import(s) found:")
        for e in all_errors:
            print(e)
        return 1
    else:
        print(f"PASS: no phantom imports in {', '.join(str(p) for p in paths)}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
