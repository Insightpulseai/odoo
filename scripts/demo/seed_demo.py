#!/usr/bin/env python3
"""Seed loader for ssot/demo/ packs.

Responsibilities:
  - Read ssot/demo/manifest.yaml
  - Validate load order + dependencies (acyclic, topological)
  - Load packs in order
  - Enforce idempotency by external key (upsert semantics)
  - Support --all, --pack <name>, --dry-run
  - Emit a summary of created/updated/skipped rows per pack
"""
from __future__ import annotations

import argparse
import importlib
import pathlib
import sys
from collections import defaultdict
from typing import Any

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DEMO_DIR = REPO_ROOT / "ssot" / "demo"
MANIFEST_PATH = DEMO_DIR / "manifest.yaml"

# Make `scripts.demo.*` importable when invoking via `python scripts/demo/seed_demo.py`.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class SeedError(RuntimeError):
    pass


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def topological_order(packs: dict[str, dict]) -> list[str]:
    """Kahn's algorithm. Raise on cycle or missing dep."""
    in_degree: dict[str, int] = {name: 0 for name in packs}
    deps_of: dict[str, list[str]] = defaultdict(list)
    for name, meta in packs.items():
        for dep in meta.get("depends_on", []):
            if dep not in packs:
                raise SeedError(f"Pack {name!r} depends on unknown {dep!r}")
            deps_of[dep].append(name)
            in_degree[name] += 1

    ready = [name for name, deg in in_degree.items() if deg == 0]
    order: list[str] = []
    while ready:
        ready.sort()
        name = ready.pop(0)
        order.append(name)
        for dependent in deps_of[name]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(packs):
        stuck = [n for n, d in in_degree.items() if d > 0]
        raise SeedError(f"Dependency cycle detected involving: {stuck}")
    return order


def load_pack(pack_name: str, dry_run: bool) -> dict[str, int]:
    """Delegate to the pack-specific seeder module if present.

    Returns counters: {created, updated, skipped}.
    """
    module_name = f"scripts.demo.seed_pack_{pack_name.replace('-', '_')}"
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        print(f"  [skip] {pack_name}: no seeder module {module_name}")
        return {"created": 0, "updated": 0, "skipped": 0}
    if not hasattr(mod, "seed"):
        raise SeedError(f"{module_name} missing seed() entrypoint")
    return mod.seed(pack_dir=DEMO_DIR / pack_name, dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Odoo demo packs")
    parser.add_argument("--all", action="store_true", help="Load every pack")
    parser.add_argument("--pack", help="Load a single pack (and its deps)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not (args.all or args.pack):
        parser.error("specify --all or --pack <name>")

    manifest = load_yaml(MANIFEST_PATH)
    packs = manifest.get("packs", {})
    if not packs:
        raise SeedError("no packs declared in manifest")

    order = topological_order(packs)
    declared_order = manifest.get("load_order", [])
    if declared_order and declared_order != order:
        raise SeedError(
            f"manifest load_order {declared_order} conflicts with topo order {order}"
        )

    if args.pack:
        if args.pack not in packs:
            raise SeedError(f"unknown pack: {args.pack}")
        wanted = {args.pack}
        queue = [args.pack]
        while queue:
            current = queue.pop()
            for dep in packs[current].get("depends_on", []):
                if dep not in wanted:
                    wanted.add(dep)
                    queue.append(dep)
        selected = [name for name in order if name in wanted]
    else:
        selected = order

    totals = {"created": 0, "updated": 0, "skipped": 0}
    for pack_name in selected:
        print(f"[pack] {pack_name} (dry_run={args.dry_run})")
        counters = load_pack(pack_name, args.dry_run)
        for k, v in counters.items():
            totals[k] = totals.get(k, 0) + v
        print(f"  -> created={counters['created']} updated={counters['updated']} skipped={counters['skipped']}")

    print(
        f"\nsummary: created={totals['created']} "
        f"updated={totals['updated']} skipped={totals['skipped']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
