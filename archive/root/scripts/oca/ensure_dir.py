#!/usr/bin/env python3
"""
ensure_dir.py

Ensures addons/oca directory exists and is writable.
Run before gitaggregate to prevent permission errors.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    target = repo_root / "addons" / "oca"

    # Create directory if it doesn't exist
    target.mkdir(parents=True, exist_ok=True)

    # Write test file to assert write permissions deterministically
    probe = target / ".write_probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except PermissionError as e:
        print(f"❌ addons/oca exists but is not writable: {e}")
        print(f"   Path: {target}")
        print("   Fix: Check filesystem permissions")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error testing write access: {e}")
        return 1

    print(f"✅ addons/oca is writable: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
