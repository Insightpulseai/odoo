#!/usr/bin/env python3
"""Validate Plane Clarity PPM SSOT contract and taxonomy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "ssot/plane/contracts/clarity_ppm.v1.yaml"
SCHEMA_PATH = REPO_ROOT / "ssot/plane/schema.plane-clarity-ppp.v1.json"
REPORT_PATH = REPO_ROOT / "artifacts/plane/ssot/validation_report.json"


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate.resolve()
    return REPO_ROOT.resolve()


def resolve_input_path(raw: str, repo_root: Path) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p

    candidates = [Path.cwd() / p, repo_root / p]
    if repo_root.name == "odoo":
        candidates.append(repo_root.parent / p)
        if p.parts and p.parts[0] == "odoo":
            candidates.append(repo_root / Path(*p.parts[1:]))

    for c in candidates:
        if c.exists():
            return c.resolve()
    return (repo_root / p).resolve()


def resolve_output_path(raw: str, repo_root: Path) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    if p.parts and p.parts[0] == "odoo" and repo_root.name == "odoo":
        p = Path(*p.parts[1:])
    return (repo_root / p).resolve()


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected object at top level")
    return data


def validate_contract_schema(contract: dict[str, Any], schema: dict[str, Any], errors: list[str]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        errors.append("jsonschema package missing; install jsonschema")
        return

    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(contract), key=lambda e: list(e.path)):
        loc = ".".join(str(x) for x in err.path) or "$"
        errors.append(f"contract:{loc}: {err.message}")


def validate_taxonomy(contract: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    checked: dict[str, Any] = {}
    refs = contract.get("contract", {}).get("taxonomy_refs", {})

    def load_ref(key: str) -> dict[str, Any]:
        rel = refs.get(key)
        if not isinstance(rel, str):
            errors.append(f"taxonomy_refs.{key} missing")
            return {}
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append(f"taxonomy file missing: {rel}")
            return {}
        checked[key] = rel
        return load_yaml(path)

    labels = load_ref("labels").get("labels", [])
    modules = load_ref("modules").get("modules", [])
    states = load_ref("states").get("states", [])
    cycles_doc = load_ref("cycles")

    gov = contract.get("governance", {})
    prefixes = gov.get("required_label_prefixes", [])
    required_states = set(gov.get("required_states", []))

    for prefix in prefixes:
        if not any(isinstance(lbl, str) and lbl.startswith(prefix) for lbl in labels):
            errors.append(f"missing required label prefix coverage: {prefix}")

    module_pat = gov.get("module_prefix_pattern")
    if isinstance(module_pat, str):
        rx = re.compile(module_pat)
        for mod in modules:
            if not isinstance(mod, str) or not rx.search(mod):
                errors.append(f"module violates prefix pattern '{module_pat}': {mod}")

    missing_states = sorted(required_states - set(states))
    if missing_states:
        errors.append(f"missing required states: {', '.join(missing_states)}")

    cycle_pat = gov.get("cycle_naming_pattern")
    cycle_names = cycles_doc.get("cycles", [])
    if isinstance(cycle_pat, str):
        c_rx = re.compile(cycle_pat)
        for cyc in cycle_names:
            if not isinstance(cyc, str) or not c_rx.match(cyc):
                errors.append(f"cycle name violates pattern '{cycle_pat}': {cyc}")

    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(CONTRACT_PATH))
    parser.add_argument("--schema", default=str(SCHEMA_PATH))
    parser.add_argument("--report", default=str(REPORT_PATH))
    args = parser.parse_args()

    errors: list[str] = []
    checked_files: dict[str, Any] = {}

    repo_root = find_repo_root(Path(__file__).resolve().parent)
    contract_path = resolve_input_path(args.contract, repo_root)
    schema_path = resolve_input_path(args.schema, repo_root)

    if not contract_path.exists():
        print(f"missing contract: {contract_path}", file=sys.stderr)
        return 2
    if not schema_path.exists():
        print(f"missing schema: {schema_path}", file=sys.stderr)
        return 2

    contract = load_yaml(contract_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    checked_files["contract"] = str(contract_path.relative_to(repo_root))
    checked_files["schema"] = str(schema_path.relative_to(repo_root))

    validate_contract_schema(contract, schema, errors)
    checked_tax = validate_taxonomy(contract, errors)
    checked_files.update({f"taxonomy_{k}": v for k, v in checked_tax.items()})

    report = {
        "status": "ok" if not errors else "failed",
        "errors": errors,
        "checked_files": checked_files,
    }

    report_path = resolve_output_path(args.report, repo_root)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        print("Plane SSOT validation failed:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1

    print("Plane SSOT validation passed.")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
