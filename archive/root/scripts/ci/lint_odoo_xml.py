#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Avoid external deps: use stdlib xml parser
# (This catches unescaped '&' and other well-formedness issues.)
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]

# Tune scopes if needed (keep conservative to avoid parsing non-XML files)
GLOBS = [
    "addons/ipai/**/*.xml",
    "addons/*/**/*.xml",  # optional if you vendor core addons
    "external-src/**/*.xml",  # optional if you want to lint OCA sources too
]

# Optional excludes (generated, vendor, etc.)
EXCLUDE_SUBSTRINGS = [
    "/.git/",
    "/node_modules/",
    "/dist/",
    "/build/",
    "/.terraform/",
]


def should_skip(p: Path) -> bool:
    s = str(p)
    return any(x in s for x in EXCLUDE_SUBSTRINGS)


def parse_xml(p: Path) -> tuple[bool, str]:
    try:
        ET.parse(p)
        return True, ""
    except ET.ParseError as e:
        return False, f"{p}: {e}"


def main() -> int:
    files: list[Path] = []
    for g in GLOBS:
        files.extend(ROOT.glob(g))

    # Dedup + deterministic order
    files = sorted({p for p in files if p.is_file() and not should_skip(p)})

    if not files:
        print("No XML files found to lint.")
        return 0

    errors: list[str] = []
    for p in files:
        ok, msg = parse_xml(p)
        if not ok:
            errors.append(msg)

    if errors:
        print("XML LINT FAILED:")
        for e in errors:
            print(" -", e)
        return 1

    print(f"XML LINT OK: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
