#!/usr/bin/env python3
"""
reset_generated_dir.py

Deterministic cleanup/reset for the generated OCA directory.
Use when the folder accidentally becomes a nested git repo or has leftover state.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    oca_dir = repo_root / "addons" / "oca"

    if oca_dir.exists():
        print(f"🗑️  Removing existing OCA dir: {oca_dir}")
        shutil.rmtree(oca_dir)

    oca_dir.mkdir(parents=True, exist_ok=True)

    # Verify writability
    probe = oca_dir / ".write_probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception as e:
        print(f"❌ Failed to verify write access: {e}")
        return 1

    print(f"✅ Reset generated OCA dir: {oca_dir}")
    print(f"   Ready for: gitaggregate -c oca-aggregate.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
