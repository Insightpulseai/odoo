"""Pack 900-pulser-demo seeder (stub).

Pulser scenario rows must reference lower-pack fixture keys. The stub
validates referential integrity before handing off to Odoo upsert.
"""
from __future__ import annotations

import pathlib

import yaml

PACK_FILES = [
    "pulser-scenarios.yaml",
    "prompt-fixtures.yaml",
    "eval-fixtures.yaml",
    "demo-routes.yaml",
]

# Hard-coded for now; production version should resolve from lower-pack yaml.
LOWER_PACK_KEYS = {
    "ic_ready_001", "ic_blocked_001",
    "bir2307_ready_001", "bir2307_blocked_001",
    "fitout_ready_001", "fitout_blocked_001",
}


def seed(pack_dir: pathlib.Path, dry_run: bool) -> dict[str, int]:
    skipped = 0
    scenarios_path = pack_dir / "pulser-scenarios.yaml"
    if scenarios_path.exists():
        payload = yaml.safe_load(scenarios_path.read_text(encoding="utf-8")) or {}
        for row in payload.get("scenarios", []):
            source = row.get("source_record")
            if source and source not in LOWER_PACK_KEYS:
                raise RuntimeError(
                    f"Pulser scenario {row['key']!r} references unknown "
                    f"lower-pack record {source!r}"
                )
    for name in PACK_FILES:
        path = pack_dir / name
        if not path.exists():
            continue
        rows_wrap = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        top = next(iter(rows_wrap.values())) if rows_wrap else []
        for _row in top if isinstance(top, list) else []:
            skipped += 1
    return {"created": 0, "updated": 0, "skipped": skipped}
