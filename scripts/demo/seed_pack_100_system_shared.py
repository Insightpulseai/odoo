"""Pack 100-system-shared seeder.

Reads fixture YAML files and upserts via Odoo. This module is a stub that
enforces the read/validate contract; wire actual Odoo ORM calls via XML-RPC
or odoo shell in a follow-up task.
"""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

PACK_FILES = [
    "companies.yaml",
    "currencies.yaml",
    "journals.yaml",
    "taxes.yaml",
    "partners-shared.yaml",
    "dms-taxonomy.yaml",
    "project-templates.yaml",
]


def load_fixtures(pack_dir: pathlib.Path) -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {}
    for name in PACK_FILES:
        path = pack_dir / name
        if not path.exists():
            continue
        content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        top = next(iter(content.values())) if content else []
        data[name] = top if isinstance(top, list) else []
    return data


def seed(pack_dir: pathlib.Path, dry_run: bool) -> dict[str, int]:
    fixtures = load_fixtures(pack_dir)
    created = updated = skipped = 0
    for file_name, rows in fixtures.items():
        for row in rows:
            # TODO: wire to Odoo XML-RPC / Odoo shell via external-key upsert.
            # Contract:
            #   - lookup by stable external key (row["key"])
            #   - create if missing, update only declared fields if present,
            #     skip if identical
            if dry_run:
                skipped += 1
            else:
                skipped += 1  # stub: no ORM wiring yet
    return {"created": created, "updated": updated, "skipped": skipped}
