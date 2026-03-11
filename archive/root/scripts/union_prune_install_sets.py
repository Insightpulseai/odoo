#!/usr/bin/env python3
"""
Union multiple install set files and optionally prune.

Reads one or more *.txt install set files (module names, comments allowed),
scans addons roots to identify known modules and dependencies, then:

- --expand-deps: include transitive deps for scanned modules
- --prune-core: remove modules not in scanned roots (assumed core)
- --prune-redundant: keep only seed modules + required dep closure
- --stable-order: deterministic topo-sorted output

Usage:
    python3 scripts/union_prune_install_sets.py \
        --set config/install_sets/ppm_parity_autogen.txt \
        --set config/install_sets/dms_parity_autogen.txt \
        --set config/install_sets/helpdesk_parity_autogen.txt \
        --set config/install_sets/ocr_parity_autogen.txt \
        --addons-root vendor/oca --addons-root addons/ipai --addons-root addons \
        --expand-deps --prune-redundant --stable-order \
        --out config/install_sets/mega_parity_autogen.txt
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


MANIFEST_FILES = ("__manifest__.py", "__openerp__.py")


@dataclass(frozen=True)
class ModuleInfo:
    name: str
    path: Path
    depends: Tuple[str, ...]


def _read_set_file(p: Path) -> List[str]:
    out: List[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def _read_manifest_dict(path: Path) -> dict:
    src = path.read_text(encoding="utf-8", errors="ignore")
    node = ast.parse(src, filename=str(path))

    if node.body and isinstance(node.body[-1], ast.Expr) and isinstance(
        node.body[-1].value, ast.Dict
    ):
        return ast.literal_eval(node.body[-1].value)

    for stmt in reversed(node.body):
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Dict):
            try:
                return ast.literal_eval(stmt.value)
            except Exception:
                pass

    raise ValueError(f"Cannot parse manifest as literal dict: {path}")


def _scan_dir_for_modules(directory: Path) -> Dict[str, ModuleInfo]:
    mods: Dict[str, ModuleInfo] = {}
    if not directory.exists() or not directory.is_dir():
        return mods
    for entry in sorted(directory.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        mf = None
        for f in MANIFEST_FILES:
            p = entry / f
            if p.exists():
                mf = p
                break
        if not mf:
            continue
        try:
            manifest = _read_manifest_dict(mf)
        except (ValueError, SyntaxError):
            continue
        depends = manifest.get("depends", []) or []
        if not isinstance(depends, (list, tuple)):
            depends = []
        mods[entry.name] = ModuleInfo(
            name=entry.name,
            path=entry,
            depends=tuple(str(d).strip() for d in depends if str(d).strip()),
        )
    return mods


def _find_modules(roots: List[Path]) -> Dict[str, ModuleInfo]:
    modules: Dict[str, ModuleInfo] = {}
    for root in roots:
        if not root.exists():
            continue
        direct = _scan_dir_for_modules(root)
        for name, info in direct.items():
            if name not in modules:
                modules[name] = info
        for subdir in sorted(root.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith("."):
                continue
            if any((subdir / mf).exists() for mf in MANIFEST_FILES):
                continue
            nested = _scan_dir_for_modules(subdir)
            for name, info in nested.items():
                if name not in modules:
                    modules[name] = info
    return modules


def _expand_deps(seeds: Set[str], mods: Dict[str, ModuleInfo]) -> Set[str]:
    expanded = set(seeds)
    changed = True
    while changed:
        changed = False
        for m in list(expanded):
            mi = mods.get(m)
            if not mi:
                continue
            for dep in mi.depends:
                if dep not in expanded:
                    expanded.add(dep)
                    changed = True
    return expanded


def _topo_order(all_set: Set[str], mods: Dict[str, ModuleInfo]) -> List[str]:
    known = {m for m in all_set if m in mods}
    unknown = sorted(m for m in all_set if m not in mods)

    indeg: Dict[str, int] = {m: 0 for m in known}
    edges: Dict[str, Set[str]] = {m: set() for m in known}

    for m in known:
        for dep in mods[m].depends:
            if dep in known:
                edges[dep].add(m)
                indeg[m] += 1

    ready = sorted(m for m, d in indeg.items() if d == 0)
    out: List[str] = []
    while ready:
        n = ready.pop(0)
        out.append(n)
        for nxt in sorted(edges[n]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
                ready.sort()

    remaining = sorted(m for m in known if m not in out)
    out.extend(remaining)
    return unknown + out


def main() -> int:
    ap = argparse.ArgumentParser(description="Union + prune install sets into a mega set")
    ap.add_argument("--set", action="append", required=True, help="Input install set file (repeatable)")
    ap.add_argument("--addons-root", action="append", required=True, help="Addons root folder (repeatable)")
    ap.add_argument("--out", required=True, help="Output mega set file")
    ap.add_argument("--comment-header", default="AUTO-GENERATED INSTALL SET: MEGA UNION", help="Header comment")
    ap.add_argument("--expand-deps", action="store_true", help="Expand dependencies transitively")
    ap.add_argument("--prune-core", action="store_true", help="Remove modules not found in scanned roots")
    ap.add_argument("--prune-redundant", action="store_true", help="Remove non-seed modules only pulled as deps")
    ap.add_argument("--stable-order", action="store_true", help="Deterministic topo-sorted ordering")
    args = ap.parse_args()

    set_files = [Path(s) for s in args.set]
    roots = [Path(r) for r in args.addons_root]

    seeds: List[str] = []
    for sf in set_files:
        if not sf.exists():
            print(f"WARNING: set file not found, skipping: {sf}")
            continue
        seeds.extend(_read_set_file(sf))

    seed_set: Set[str] = set(seeds)
    mods = _find_modules(roots)

    full: Set[str] = set(seed_set)
    if args.expand_deps:
        full = _expand_deps(full, mods)

    if args.prune_core:
        full = {m for m in full if m in mods}

    if args.prune_redundant:
        closure = _expand_deps({m for m in seed_set if m in mods}, mods)
        keep = {m for m in full if m in seed_set} | {m for m in closure if m in full}
        full = keep

    ordered = _topo_order(full, mods) if args.stable_order else sorted(full)

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# {args.comment_header}"]
    lines.append("# Generated by: scripts/union_prune_install_sets.py")
    lines.append("# Inputs:")
    for sf in set_files:
        lines.append(f"#   - {sf}")
    lines.append("# Roots:")
    for r in roots:
        lines.append(f"#   - {r}")
    lines.append(f"# Expand deps: {args.expand_deps}")
    lines.append(f"# Prune core: {args.prune_core}")
    lines.append(f"# Prune redundant: {args.prune_redundant}")
    lines.append(f"# Module count: {len(ordered)}")
    lines.append("")
    lines.extend(ordered)
    outp.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"OK: wrote {len(ordered)} modules to {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
