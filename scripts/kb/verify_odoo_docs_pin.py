#!/usr/bin/env python3
"""
Verify docs/kb/odoo19/upstream snapshot matches docs/kb/odoo19/UPSTREAM_PIN.json.

Supports two modes:
  1) upstream is a git checkout -> compare `git rev-parse HEAD` to pinned_commit
  2) upstream is a plain directory -> compare docs/kb/odoo19/UPSTREAM_REV.txt to pinned_commit

Fails loudly if:
  - pinned_commit is unset / placeholder
  - upstream missing
  - mismatch detected
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_ROOT_DEFAULT = ROOT / "docs" / "kb" / "odoo19"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _run_git(args: list[str], cwd: Path) -> str:
    out = subprocess.check_output(["git", *args], cwd=str(cwd), stderr=subprocess.STDOUT)
    return out.decode("utf-8").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", default=str(KB_ROOT_DEFAULT))
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    pin_path = kb_root / "UPSTREAM_PIN.json"
    upstream = kb_root / "upstream"
    rev_txt = kb_root / "UPSTREAM_REV.txt"

    if not pin_path.exists():
        raise SystemExit(f"Missing {pin_path}")
    if not upstream.exists():
        raise SystemExit(f"Missing upstream snapshot dir: {upstream}")

    pin = _read_json(pin_path)

    # 1. Schema Validation
    required_keys = ["upstream", "branch", "pinned_commit"]
    missing = [k for k in required_keys if not pin.get(k)]
    if missing:
        raise SystemExit(f"UPSTREAM_PIN.json missing required keys: {missing}")

    pinned = pin["pinned_commit"].strip()
    if pinned == "REPLACE_WITH_SHA":
        raise SystemExit("UPSTREAM_PIN.json pinned_commit is not set (placeholder).")

    print(f"Verifying pin: {pin['upstream']} @ {pin['branch']} ({pinned})")

    # 2. Content/Commit Verification
    # Mode 1: git checkout
    if (upstream / ".git").exists():
        head = _run_git(["rev-parse", "HEAD"], upstream)
        if head != pinned:
            raise SystemExit(
                f"UPSTREAM_PIN mismatch: upstream HEAD={head} != pinned_commit={pinned}"
            )

        # Verify remote URL matches if possible (optional, but good for anti-drift)
        try:
            remote = _run_git(["remote", "get-url", "origin"], upstream)
            # Normalize to avoid https://github.com/odoo/documentation vs .git differences
            if pin["upstream"].rstrip(".git") not in remote:
                print(
                    f"WARNING: upstream remote {remote} does not match pinned upstream {pin['upstream']}"
                )
        except Exception:
            pass

        print(f"OK: upstream git HEAD matches pinned_commit {pinned}")
        return

    # Mode 2: directory snapshot with recorded rev
    if not rev_txt.exists():
        raise SystemExit(
            f"upstream is not a git checkout and {rev_txt} is missing. "
            "Create UPSTREAM_REV.txt with the pinned commit SHA."
        )
    recorded = rev_txt.read_text(encoding="utf-8").strip()
    if recorded != pinned:
        raise SystemExit(f"UPSTREAM_REV mismatch: {recorded} != pinned_commit={pinned}")
    print(f"OK: UPSTREAM_REV.txt matches pinned_commit {pinned}")


if __name__ == "__main__":
    main()
