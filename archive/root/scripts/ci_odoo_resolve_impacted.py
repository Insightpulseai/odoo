#!/usr/bin/env python3
"""
Odoo Impacted Modules Resolver
Computes impacted modules = changed ∪ reverse_closure(changed)

This determines which modules need testing when a module changes:
- The changed modules themselves
- All modules that depend on the changed modules (transitively)

Inputs:
  - ODOO_CHANGED_MODULES_JSON: JSON list from ci_odoo_changed_modules.py
  - config/odoo/ci_policy.yml: addons_roots for scanning

Output:
  - JSON: {"impacted": [...], "impacted_csv": "a,b,c", "changed": [...], "dependents": [...]}
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        import yaml
        return yaml.safe_load(path.read_text("utf-8")) or {}
    except Exception:
        return {}


def read_text(p: Path) -> str:
    """Read file as text."""
    return p.read_text("utf-8", errors="replace")


def parse_manifest_dict(manifest_path: Path) -> dict:
    """Parse Odoo manifest file and return dict."""
    src = read_text(manifest_path)

    # Try safe eval of dict literal
    try:
        match = re.search(r"^(\{[\s\S]*\})\s*$", src, re.MULTILINE)
        if match:
            return eval(match.group(1), {"__builtins__": {}}, {})
    except Exception:
        pass

    # Try AST parsing
    try:
        import ast
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                result = {}
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant):
                        try:
                            result[key.value] = ast.literal_eval(ast.unparse(value))
                        except Exception:
                            result[key.value] = None
                if "name" in result or "depends" in result:
                    return result
    except Exception:
        pass

    raise ValueError(f"Unable to parse manifest: {manifest_path}")


def module_manifest_path(module_dir: Path) -> Optional[Path]:
    """Get manifest path for a module directory."""
    for name in ["__manifest__.py", "__openerp__.py"]:
        mp = module_dir / name
        if mp.exists():
            return mp
    return None


def discover_modules(repo_root: Path, addons_roots: list[str]) -> dict[str, Path]:
    """
    Discover all modules in addons roots.
    Returns: {module_name: module_dir_path}
    """
    idx: dict[str, Path] = {}
    for ar in addons_roots:
        root = (repo_root / ar).resolve()
        if not root.exists():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            mp = module_manifest_path(child)
            if mp:
                idx[child.name] = child
    return idx


def deps_for(module_dir: Path) -> list[str]:
    """Get list of dependencies from module manifest."""
    mp = module_manifest_path(module_dir)
    if not mp:
        return []
    try:
        d = parse_manifest_dict(mp)
        deps = d.get("depends") or []
        if isinstance(deps, (tuple, list)):
            return [str(x).strip() for x in deps if str(x).strip()]
    except Exception:
        pass
    return []


def build_reverse_dep_graph(idx: dict[str, Path]) -> dict[str, set[str]]:
    """
    Build reverse dependency graph.
    Returns: {module_name: set of modules that depend on it}
    """
    reverse: dict[str, set[str]] = {m: set() for m in idx}

    for module_name, module_dir in idx.items():
        for dep in deps_for(module_dir):
            # Only track repo-local deps
            if dep in idx:
                reverse[dep].add(module_name)

    return reverse


def reverse_closure(changed: list[str], reverse_graph: dict[str, set[str]]) -> list[str]:
    """
    Compute transitive closure of reverse dependencies.
    Returns all modules that depend (directly or transitively) on any changed module.
    """
    visited = set()
    queue = list(changed)
    dependents = []

    while queue:
        m = queue.pop(0)
        if m not in reverse_graph:
            continue
        for dependent in reverse_graph[m]:
            if dependent not in visited and dependent not in changed:
                visited.add(dependent)
                dependents.append(dependent)
                queue.append(dependent)

    return dependents


def stable_unique(seq: list[str]) -> list[str]:
    """Return list with duplicates removed, preserving order."""
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def main():
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    policy_path = repo_root / "config/odoo/ci_policy.yml"

    if not policy_path.exists():
        print(json.dumps({
            "impacted": [],
            "impacted_csv": "",
            "changed": [],
            "dependents": [],
            "error": "config/odoo/ci_policy.yml missing"
        }, indent=2))
        return

    policy = load_yaml(policy_path)
    addons_roots = policy.get("addons_roots") or [
        "addons",
        "addons/ipai",
        "oca",
    ]

    # Build module index
    idx = discover_modules(repo_root, addons_roots)
    print(f"# Discovered {len(idx)} modules in repo", file=sys.stderr)

    # Get changed modules
    changed_json = os.environ.get("ODOO_CHANGED_MODULES_JSON", "[]")
    try:
        changed = json.loads(changed_json) if changed_json.strip() else []
    except json.JSONDecodeError:
        changed = []

    changed_names = [m.get("name") for m in changed if m.get("name")]
    changed_names = stable_unique([n for n in changed_names if isinstance(n, str)])

    # Filter to repo-local modules only
    changed_in_repo = [m for m in changed_names if m in idx]

    print(f"# Changed modules in repo: {changed_in_repo}", file=sys.stderr)

    # Build reverse dependency graph
    reverse_graph = build_reverse_dep_graph(idx)

    # Compute reverse closure (dependents)
    dependents = reverse_closure(changed_in_repo, reverse_graph)
    print(f"# Dependent modules (reverse closure): {dependents}", file=sys.stderr)

    # Impacted = changed ∪ dependents
    impacted = stable_unique(changed_in_repo + dependents)

    out = {
        "impacted": impacted,
        "impacted_csv": ",".join(impacted),
        "changed": changed_in_repo,
        "dependents": dependents,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({
            "impacted": [],
            "impacted_csv": "",
            "changed": [],
            "dependents": [],
            "error": str(e)
        }, indent=2))
        sys.exit(1)
