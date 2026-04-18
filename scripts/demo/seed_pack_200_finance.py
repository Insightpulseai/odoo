"""Pack 200-finance seeder (stub — wire to Odoo in follow-up)."""
from __future__ import annotations

import pathlib

import yaml

PACK_FILES = [
    "customers.yaml",
    "vendors.yaml",
    "products-services.yaml",
    "invoices-draft.yaml",
    "vendor-bills.yaml",
    "payments.yaml",
    "intercompany-scenarios.yaml",
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
            # Invariant: must not auto-post invoices.
            # Invariant: ready + blocked pairs remain in declared state.
            skipped += 1
    return {"created": 0, "updated": 0, "skipped": skipped}
