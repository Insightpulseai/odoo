#!/usr/bin/env python3
"""
Generate curated Odoo module install sets from addons roots.

Scans addons directories, parses __manifest__.py via AST (no exec),
applies allow/deny filters, optionally expands dependencies transitively,
and outputs a deterministic, topo-sorted module list.

Usage:
    # PPM parity set (curated)
    python3 scripts/gen_install_set.py \
        --addons-root vendor/oca --addons-root vendor/oca/OCA \
        --addons-root external-src --addons-root addons/ipai --addons-root addons \
        --allow-file config/install_sets/allow_modules_ppm.txt \
        --expand-deps --include-core \
        --out config/install_sets/ppm_parity_autogen.txt

    # Full scan (deny-only)
    python3 scripts/gen_install_set.py \
        --addons-root vendor/oca --addons-root addons/ipai \
        --deny-prefix test_ --deny-prefix demo_ \
        --out config/install_sets/all_addons_autogen.txt
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


MANIFEST_FILES = ("__manifest__.py", "__openerp__.py")


@dataclass(frozen=True)
class ModuleInfo:
    name: str
    path: Path
    depends: Tuple[str, ...]
    installable: bool


def _read_manifest_dict(path: Path) -> Dict:
    """Parse manifest file as a literal dict using AST (safe, no exec)."""
    src = path.read_text(encoding="utf-8", errors="ignore")
    try:
        node = ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"Manifest syntax error in {path}: {exc}") from exc

    # Common: file is a single dict literal expression
    if node.body and isinstance(node.body[-1], ast.Expr):
        val = node.body[-1].value
        if isinstance(val, ast.Dict):
            return ast.literal_eval(val)

    # Assignment like `manifest = {...}`
    for stmt in reversed(node.body):
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Dict):
            try:
                return ast.literal_eval(stmt.value)
            except Exception:
                pass

    raise ValueError(f"Could not parse manifest dict literal in {path}")


def _scan_dir_for_modules(directory: Path) -> Dict[str, ModuleInfo]:
    """Find Odoo modules in a directory (non-recursive into module dirs)."""
    modules: Dict[str, ModuleInfo] = {}
    if not directory.exists() or not directory.is_dir():
        return modules

    for entry in sorted(directory.iterdir()):
        if not entry.is_dir():
            continue
        # Skip hidden dirs and common non-module dirs
        if entry.name.startswith(".") or entry.name in ("setup", "node_modules", "__pycache__"):
            continue

        manifest_path = None
        for mf in MANIFEST_FILES:
            p = entry / mf
            if p.exists() and p.is_file():
                manifest_path = p
                break
        if not manifest_path:
            continue

        try:
            manifest = _read_manifest_dict(manifest_path)
        except (ValueError, Exception):
            continue

        depends = manifest.get("depends", []) or []
        if not isinstance(depends, (list, tuple)):
            depends = []
        installable = manifest.get("installable", True)
        name = entry.name

        modules[name] = ModuleInfo(
            name=name,
            path=entry,
            depends=tuple(str(d).strip() for d in depends if str(d).strip()),
            installable=bool(installable),
        )
    return modules


def _find_modules(addons_roots: List[Path]) -> Dict[str, ModuleInfo]:
    """
    Scan multiple addons roots. Each root can contain:
    - Direct modules (root/module_name/__manifest__.py)
    - Repo dirs containing modules (root/repo_name/module_name/__manifest__.py)
    First-found wins (earlier roots take priority).
    """
    modules: Dict[str, ModuleInfo] = {}

    for root in addons_roots:
        if not root.exists():
            continue
        # Level 1: direct modules in root
        direct = _scan_dir_for_modules(root)
        for name, info in direct.items():
            if name not in modules:
                modules[name] = info

        # Level 2: subdirectories that are OCA repos (contain modules)
        for subdir in sorted(root.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith("."):
                continue
            # Skip if subdir is itself a module (already scanned above)
            if any((subdir / mf).exists() for mf in MANIFEST_FILES):
                continue
            nested = _scan_dir_for_modules(subdir)
            for name, info in nested.items():
                if name not in modules:
                    modules[name] = info

    return modules


def _load_list_file(path_str: Optional[str]) -> Set[str]:
    if not path_str:
        return set()
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"List file not found: {path_str}")
    out: Set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.add(s)
    return out


def _matches_prefixes(name: str, prefixes: List[str]) -> bool:
    return any(name.startswith(px) for px in prefixes)


def _expand_deps(
    selected: Set[str],
    modules: Dict[str, ModuleInfo],
) -> Set[str]:
    """Expand dependencies transitively. Unknown deps kept (assumed core)."""
    expanded = set(selected)
    changed = True
    while changed:
        changed = False
        for mod in list(expanded):
            info = modules.get(mod)
            if not info:
                continue
            for dep in info.depends:
                if dep not in expanded:
                    expanded.add(dep)
                    changed = True
    return expanded


def _topo_sort(mods: Set[str], modules: Dict[str, ModuleInfo]) -> List[str]:
    """Deterministic topo sort: known modules by dependency, unknown sorted alpha."""
    known = {m for m in mods if m in modules}
    unknown = sorted(m for m in mods if m not in modules)

    indeg: Dict[str, int] = {m: 0 for m in known}
    edges: Dict[str, Set[str]] = {m: set() for m in known}

    for mod in known:
        for dep in modules[mod].depends:
            if dep in known:
                edges[dep].add(mod)
                indeg[mod] += 1

    ready = sorted(m for m, d in indeg.items() if d == 0)
    out: List[str] = []

    while ready:
        node = ready.pop(0)
        out.append(node)
        for nxt in sorted(edges[node]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
                ready.sort()

    # Append any remaining (cycles) deterministically
    remaining = sorted(m for m in known if m not in out)
    out.extend(remaining)

    # Unknown/core modules go at the front (they're typically deps)
    return unknown + out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate curated Odoo module install sets"
    )
    ap.add_argument(
        "--addons-root", action="append", required=True,
        help="Addons root folder (repeatable). Scans for modules at 1-2 levels deep."
    )
    ap.add_argument("--allow-file", default=None, help="File with allowed module names (one per line)")
    ap.add_argument("--deny-file", default=None, help="File with denied module names (one per line)")
    ap.add_argument("--allow-prefix", action="append", default=[], help="Allow modules starting with prefix (repeatable)")
    ap.add_argument("--deny-prefix", action="append", default=[], help="Deny modules starting with prefix (repeatable)")
    ap.add_argument("--expand-deps", action="store_true", help="Include dependencies transitively")
    ap.add_argument("--include-core", action="store_true", help="Include core deps not found in scanned roots")
    ap.add_argument("--installable-only", action="store_true", default=True, help="Only include installable modules (default: true)")
    ap.add_argument("--out", required=True, help="Output .txt file path")
    ap.add_argument("--comment-header", default="AUTO-GENERATED INSTALL SET", help="Header comment")
    args = ap.parse_args()

    roots = [Path(r) for r in args.addons_root]
    all_mods = _find_modules(roots)

    allow_set = _load_list_file(args.allow_file)
    deny_set = _load_list_file(args.deny_file)

    # Initial selection: all scanned installable modules
    selected: Set[str] = set()
    for name, info in all_mods.items():
        if args.installable_only and not info.installable:
            continue
        selected.add(name)

    # Apply allow filters
    if allow_set:
        selected = {m for m in selected if m in allow_set}
    if args.allow_prefix:
        selected = {m for m in selected if _matches_prefixes(m, args.allow_prefix)}

    # Apply deny filters
    if deny_set:
        selected = {m for m in selected if m not in deny_set}
    if args.deny_prefix:
        selected = {m for m in selected if not _matches_prefixes(m, args.deny_prefix)}

    # Expand deps transitively
    if args.expand_deps:
        selected = _expand_deps(selected, all_mods)
        # Re-apply deny after expansion (don't pull in denied deps)
        if deny_set:
            selected = {m for m in selected if m not in deny_set}
        if args.deny_prefix:
            selected = {m for m in selected if not _matches_prefixes(m, args.deny_prefix)}

    # If not including core deps, remove unknowns
    if not args.include_core:
        selected = {m for m in selected if m in all_mods}

    ordered = _topo_sort(selected, all_mods)

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# {args.comment_header}")
    lines.append(f"# Generated by: scripts/gen_install_set.py")
    lines.append(f"# Roots:")
    for r in roots:
        lines.append(f"#   - {r}")
    if args.allow_file:
        lines.append(f"# Allow file: {args.allow_file}")
    if args.deny_file:
        lines.append(f"# Deny file: {args.deny_file}")
    if args.allow_prefix:
        lines.append(f"# Allow prefix: {', '.join(args.allow_prefix)}")
    if args.deny_prefix:
        lines.append(f"# Deny prefix: {', '.join(args.deny_prefix)}")
    lines.append(f"# Expand deps: {args.expand_deps}")
    lines.append(f"# Module count: {len(ordered)}")
    lines.append("")
    lines.extend(ordered)
    outp.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"OK: wrote {len(ordered)} modules to {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
