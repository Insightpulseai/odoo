"""Contract tests for ssot/demo/manifest.yaml + pack graph."""
from __future__ import annotations

import pathlib

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DEMO_DIR = REPO_ROOT / "ssot" / "demo"
MANIFEST = yaml.safe_load((DEMO_DIR / "manifest.yaml").read_text(encoding="utf-8"))


def test_manifest_has_packs():
    assert MANIFEST.get("packs"), "manifest must declare packs"


def test_manifest_load_order_matches_packs():
    load_order = MANIFEST.get("load_order", [])
    packs = MANIFEST.get("packs", {})
    assert set(load_order) == set(packs.keys()), \
        f"load_order {load_order} and packs {list(packs)} must be same set"


def test_all_pack_dirs_exist():
    for pack in MANIFEST["packs"]:
        assert (DEMO_DIR / pack).is_dir(), f"missing pack dir: {pack}"


def test_all_pack_manifests_exist_and_match():
    for pack in MANIFEST["packs"]:
        path = DEMO_DIR / pack / "manifest.yaml"
        assert path.exists(), f"missing {path}"
        pack_manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert pack_manifest["pack"] == pack, \
            f"pack name mismatch in {path}: {pack_manifest['pack']!r} vs {pack!r}"


def test_dependencies_resolve():
    packs = MANIFEST["packs"]
    for name, meta in packs.items():
        for dep in meta.get("depends_on", []):
            assert dep in packs, f"pack {name} depends on unknown {dep}"


def test_dependency_graph_acyclic():
    """Kahn's algorithm: if topo order consumes all nodes, graph is acyclic."""
    packs = MANIFEST["packs"]
    in_deg = {n: 0 for n in packs}
    edges: dict[str, list[str]] = {n: [] for n in packs}
    for name, meta in packs.items():
        for dep in meta.get("depends_on", []):
            edges[dep].append(name)
            in_deg[name] += 1
    ready = [n for n, d in in_deg.items() if d == 0]
    consumed = 0
    while ready:
        n = ready.pop()
        consumed += 1
        for m in edges[n]:
            in_deg[m] -= 1
            if in_deg[m] == 0:
                ready.append(m)
    assert consumed == len(packs), "dependency graph has a cycle"


def test_load_order_respects_dependencies():
    packs = MANIFEST["packs"]
    order = MANIFEST["load_order"]
    position = {name: i for i, name in enumerate(order)}
    for name, meta in packs.items():
        for dep in meta.get("depends_on", []):
            assert position[dep] < position[name], \
                f"{dep} (position {position[dep]}) must precede {name} (position {position[name]})"


def test_unique_scenario_keys_across_packs():
    """No two scenario/fixture records across packs can share an external key."""
    seen: dict[str, str] = {}
    for pack in MANIFEST["packs"]:
        for yaml_file in (DEMO_DIR / pack).glob("*.yaml"):
            if yaml_file.name == "manifest.yaml":
                continue
            payload = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
            if not isinstance(payload, dict):
                continue
            top = next(iter(payload.values())) if payload else []
            if not isinstance(top, list):
                continue
            for row in top:
                if not isinstance(row, dict):
                    continue
                key = row.get("key")
                if not key:
                    continue
                if key in seen:
                    pytest.fail(
                        f"duplicate external key {key!r}: "
                        f"first seen in {seen[key]}, repeated in {pack}/{yaml_file.name}"
                    )
                seen[key] = f"{pack}/{yaml_file.name}"
