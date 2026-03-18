#!/usr/bin/env python3
"""
Vendor Odoo docs (odoo/documentation branch 19.0) into docs/kb/odoo19/upstream/.

Design goals:
  - deterministic directory snapshot
  - updates UPSTREAM_PIN.json + UPSTREAM_REV.txt
  - no UI steps

Behavior:
  - clones to a temp dir
  - checks out the provided commit (or resolves latest on branch)
  - exports only text docs (.md/.rst/.txt) + keeps paths intact
  - writes UPSTREAM_REV.txt with the exact commit
  - updates pinned_commit + pinned_at_utc

Note:
  - This is a build/vendor tool; it requires `git` in PATH.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_ROOT_DEFAULT = ROOT / "docs" / "kb" / "odoo19"

UPSTREAM_URL_DEFAULT = "https://github.com/odoo/documentation"
BRANCH_DEFAULT = "19.0"

ALLOWED_SUFFIX = {".md", ".rst", ".txt"}


def _run(args: list[str], cwd: Path | None = None) -> str:
    out = subprocess.check_output(args, cwd=str(cwd) if cwd else None, stderr=subprocess.STDOUT)
    return out.decode("utf-8").strip()


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy_filtered(src: Path, dst: Path) -> int:
    count = 0
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in ALLOWED_SUFFIX:
            continue
        rel = p.relative_to(src)
        outp = dst / rel
        outp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, outp)
        count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", default=str(KB_ROOT_DEFAULT))
    ap.add_argument("--upstream-url", default=UPSTREAM_URL_DEFAULT)
    ap.add_argument("--branch", default=BRANCH_DEFAULT)
    ap.add_argument("--commit", default="", help="Optional explicit commit SHA to pin")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    pin_path = kb_root / "UPSTREAM_PIN.json"
    upstream_dir = kb_root / "upstream"
    rev_txt = kb_root / "UPSTREAM_REV.txt"

    kb_root.mkdir(parents=True, exist_ok=True)
    if not pin_path.exists():
        # create a minimal pin file if absent
        _write_json(
            pin_path,
            {
                "upstream": args.upstream_url,
                "branch": args.branch,
                "pinned_commit": "REPLACE_WITH_SHA",
                "pinned_at_utc": "REPLACE_WITH_UTC",
            },
        )

    pin = _read_json(pin_path)
    pin["upstream"] = args.upstream_url
    pin["branch"] = args.branch

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        repo = td_path / "documentation"
        _run(["git", "clone", "--filter=blob:none", "--no-checkout", args.upstream_url, str(repo)])
        _run(["git", "fetch", "origin", args.branch], cwd=repo)

        commit = args.commit.strip()
        if not commit:
            commit = _run(["git", "rev-parse", f"origin/{args.branch}"], cwd=repo)

        _run(["git", "checkout", "--detach", commit], cwd=repo)

        # Replace upstream snapshot atomically
        staged = td_path / "snapshot"
        staged.mkdir(parents=True, exist_ok=True)
        copied = _copy_filtered(repo, staged)

        tmp_target = kb_root / ".upstream_tmp"
        if tmp_target.exists():
            shutil.rmtree(tmp_target)
        shutil.copytree(staged, tmp_target)

        if upstream_dir.exists():
            shutil.rmtree(upstream_dir)
        tmp_target.rename(upstream_dir)

    rev_txt.write_text(commit + "\n", encoding="utf-8")
    pin["pinned_commit"] = commit
    pin["pinned_at_utc"] = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    _write_json(pin_path, pin)

    print(f"Vendored {copied} files into {upstream_dir}")
    print(f"Pinned commit: {commit}")


if __name__ == "__main__":
    main()
