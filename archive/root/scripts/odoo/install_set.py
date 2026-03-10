#!/usr/bin/env python3
"""Validate and plan Odoo install sets (CI-safe dry-run)."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SET = REPO_ROOT / "ssot/odoo/install_sets/finops_ppm.yaml"
DEFAULT_LOCK = REPO_ROOT / "ssot/odoo/oca_lock.yaml"
DEFAULT_REPORT = REPO_ROOT / "artifacts/odoo/install_sets/finops_ppm_report.json"


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML top-level object required: {path}")
    return data


def parse_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    try:
        node = ast.parse(text)
    except Exception:
        return {}

    for stmt in node.body:
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.Dict, ast.Constant, ast.List, ast.Tuple)):
            try:
                obj = ast.literal_eval(stmt.value)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
        if isinstance(stmt, ast.Expr):
            try:
                obj = ast.literal_eval(stmt.value)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
    return {}


def discover_modules(root: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for manifest in root.rglob("__manifest__.py"):
        module_dir = manifest.parent
        module_name = module_dir.name
        meta = parse_manifest(manifest)
        depends = meta.get("depends") if isinstance(meta.get("depends"), list) else []
        index[module_name] = {
            "manifest": str(manifest.relative_to(root)),
            "path": str(module_dir.relative_to(root)),
            "depends": [d for d in depends if isinstance(d, str)],
        }
    return index


def ordered_modules(spec: dict[str, Any]) -> list[str]:
    tiers = spec.get("module_tiers", {})
    policy = spec.get("policy", {})
    order = policy.get("install_order", ["core", "oca", "ipai", "meta"])
    out: list[str] = []
    seen = set()
    for tier in order:
        for mod in tiers.get(tier, []) or []:
            if isinstance(mod, str) and mod not in seen:
                seen.add(mod)
                out.append(mod)
    return out


def validate_oca_lock(lock: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    repos = lock.get("repos", [])
    if not isinstance(repos, list) or not repos:
        return ["oca_lock.yaml must define a non-empty repos list"]

    for idx, repo in enumerate(repos):
        if not isinstance(repo, dict):
            errors.append(f"oca_lock repos[{idx}] must be an object")
            continue
        for key in ("name", "target_path", "ref"):
            if not repo.get(key):
                errors.append(f"oca_lock repos[{idx}] missing required key '{key}'")
        target = repo.get("target_path")
        if target:
            target_path = root / str(target)
            if not target_path.exists():
                errors.append(f"oca_lock target path missing: {target}")
    return errors


def build_report(
    spec: dict[str, Any],
    module_index: dict[str, dict[str, Any]],
    selected: list[str],
    missing: list[str],
    missing_deps: dict[str, list[str]],
    lock_errors: list[str],
) -> dict[str, Any]:
    selected_set = set(selected)
    excluded = [m for m in sorted(module_index.keys()) if m not in selected_set]
    return {
        "install_set_id": spec.get("install_set_id"),
        "name": spec.get("name"),
        "schema": spec.get("schema"),
        "constraints": spec.get("constraints", {}),
        "selected_modules": selected,
        "missing_modules": missing,
        "missing_runtime_deps": missing_deps,
        "oca_lock_errors": lock_errors,
        "included_count": len(selected),
        "excluded_count": len(excluded),
        "excluded_modules": excluded,
        "status": "ok" if not (missing or missing_deps or lock_errors) else "failed",
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-file", default=str(DEFAULT_SET), help="Install set YAML")
    parser.add_argument("--oca-lock", default=str(DEFAULT_LOCK), help="OCA lock YAML")
    parser.add_argument("--db", default="", help="Target DB name for reporting context")
    parser.add_argument("--dry-run", action="store_true", help="Validate and emit plan only")
    parser.add_argument("--apply", action="store_true", help="Execute install/upgrade (disabled in Endpoint A)")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="JSON report output path")
    args = parser.parse_args()

    if args.dry_run == args.apply:
        print("Use exactly one of --dry-run or --apply", file=sys.stderr)
        return 2
    if args.apply:
        print("--apply is disabled for Endpoint A (CI verification only)", file=sys.stderr)
        return 2

    set_path = Path(args.set_file)
    lock_path = Path(args.oca_lock)
    if not set_path.exists() or not lock_path.exists():
        print("Missing set or lock file", file=sys.stderr)
        return 2

    spec = load_yaml(set_path)
    lock = load_yaml(lock_path)

    errors: list[str] = []
    if spec.get("schema") != "ssot.odoo.install_set.v1":
        errors.append("install set schema must be ssot.odoo.install_set.v1")
    if lock.get("schema") != "ssot.odoo.oca_lock.v1":
        errors.append("oca lock schema must be ssot.odoo.oca_lock.v1")

    lock_errors = validate_oca_lock(lock, REPO_ROOT)

    modules = discover_modules(REPO_ROOT / "addons")
    selected = ordered_modules(spec)
    missing = [m for m in selected if m not in modules]

    core_allow = set((spec.get("policy", {}).get("core_dep_allowlist", []) or []))
    selected_set = set(selected)
    missing_deps: dict[str, list[str]] = {}
    for mod in selected:
        if mod not in modules:
            continue
        deps = modules[mod].get("depends", [])
        unresolved: list[str] = []
        for dep in deps:
            if dep in selected_set or dep in modules or dep in core_allow:
                continue
            unresolved.append(dep)
        if unresolved:
            missing_deps[mod] = sorted(set(unresolved))

    report = build_report(spec, modules, selected, missing, missing_deps, lock_errors + errors)
    report["db"] = args.db or None
    report["mode"] = "dry-run"
    report["set_file"] = str(set_path)
    report["oca_lock"] = str(lock_path)

    write_report(Path(args.report), report)

    if report["status"] != "ok":
        print("Install set verification failed. See report:", args.report, file=sys.stderr)
        return 1

    print("Install set verification passed.")
    print("Report:", args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
