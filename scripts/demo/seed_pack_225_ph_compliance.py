"""Pack 225-ph-compliance seeder (stub)."""
from __future__ import annotations

import pathlib

import yaml

PACK_FILES = [
    "withholding-partners.yaml",
    "bir2307-scenarios.yaml",
    "tin-atc-fixtures.yaml",
    "blocked-vs-ready.yaml",
]


def seed(pack_dir: pathlib.Path, dry_run: bool) -> dict[str, int]:
    skipped = 0
    for name in PACK_FILES:
        path = pack_dir / name
        if not path.exists():
            continue
        rows_wrap = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        top = next(iter(rows_wrap.values())) if rows_wrap else []
        for _row in top if isinstance(top, list) else []:
            # Invariant: 2307 blocked case must not become releasable on re-run.
            skipped += 1
    return {"created": 0, "updated": 0, "skipped": skipped}
