"""Pack 250-fitout-docs seeder (stub)."""
from __future__ import annotations

import pathlib

import yaml

PACK_FILES = [
    "fitout-requests.yaml",
    "checklist-templates.yaml",
    "corporate-docs-catalog.yaml",
    "submission-states.yaml",
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
            # Invariant: blocked request must retain its missing-docs list on re-run.
            skipped += 1
    return {"created": 0, "updated": 0, "skipped": skipped}
