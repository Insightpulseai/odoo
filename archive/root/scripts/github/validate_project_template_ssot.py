#!/usr/bin/env python3
"""Validate GitHub Project template SSOT files."""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = REPO_ROOT / "ssot/github/projects/templates/schema.project-template.v1.json"
DEFAULT_GLOB = "ssot/github/projects/templates/*.project.yaml"


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def jsonschema_validate(instance: Any, schema: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return [
            "jsonschema package is required for schema validation. "
            "Install with: pip install jsonschema"
        ]

    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        loc = ".".join(str(x) for x in err.path) or "$"
        errors.append(f"{path}:{loc}: {err.message}")
    return errors


def policy_validate(spec: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []

    required_field_keys = {"status", "priority"}
    fields = spec.get("fields") or []
    seen_keys: set[str] = set()
    seen_names: set[str] = set()

    if not isinstance(fields, list) or not fields:
        errors.append(f"{path}:fields: must include at least one field")
        return errors

    for idx, field in enumerate(fields):
        fpath = f"{path}:fields[{idx}]"
        if not isinstance(field, dict):
            errors.append(f"{fpath}: must be an object")
            continue

        key = field.get("key")
        name = field.get("name")
        ftype = field.get("type")

        if key in seen_keys:
            errors.append(f"{fpath}.key: duplicate key '{key}'")
        else:
            seen_keys.add(str(key))

        if name in seen_names:
            errors.append(f"{fpath}.name: duplicate field name '{name}'")
        else:
            seen_names.add(str(name))

        if ftype == "SINGLE_SELECT":
            options = field.get("options") or []
            option_names = [o.get("name") for o in options if isinstance(o, dict)]
            if len(option_names) != len(set(option_names)):
                errors.append(f"{fpath}.options: duplicate option names are not allowed")

        if ftype not in {"SINGLE_SELECT", "TEXT", "NUMBER", "DATE", "ITERATION"}:
            errors.append(f"{fpath}.type: unsupported type '{ftype}'")

    missing_core = sorted(required_field_keys - seen_keys)
    if missing_core:
        errors.append(f"{path}: missing required core fields: {', '.join(missing_core)}")

    template_id = spec.get("template_id")
    slug = ((spec.get("project") or {}).get("slug"))
    if isinstance(template_id, str) and isinstance(slug, str):
        expected_slug = template_id.replace("_", "-")
        if slug != expected_slug:
            errors.append(
                f"{path}:project.slug '{slug}' must match template_id '{template_id}' -> '{expected_slug}'"
            )

    return errors


def expand_specs(patterns: list[str]) -> list[Path]:
    out: list[Path] = []
    for pattern in patterns:
        matches = sorted(Path(p) for p in glob.glob(pattern))
        if matches:
            out.extend(matches)
        else:
            candidate = Path(pattern)
            if candidate.exists():
                out.append(candidate)
    dedup = sorted({p.resolve() for p in out})
    return dedup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        action="append",
        default=[DEFAULT_GLOB],
        help="Template path or glob (can be repeated)",
    )
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Schema file path")
    parser.add_argument("--json-output", default="", help="Optional output JSON report path")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        return 2

    specs = expand_specs(args.spec)
    if not specs:
        print("No template specs matched.", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    report: dict[str, Any] = {
        "ok": True,
        "schema": str(schema_path),
        "checked": [str(p) for p in specs],
        "errors": [],
    }

    for spec_path in specs:
        try:
            data = load_yaml(spec_path)
        except Exception as exc:  # pragma: no cover
            report["ok"] = False
            report["errors"].append(f"{spec_path}: failed to parse YAML: {exc}")
            continue

        if not isinstance(data, dict):
            report["ok"] = False
            report["errors"].append(f"{spec_path}: top-level YAML must be an object")
            continue

        schema_errors = jsonschema_validate(data, schema, spec_path)
        policy_errors = policy_validate(data, spec_path)
        all_errors = schema_errors + policy_errors
        if all_errors:
            report["ok"] = False
            report["errors"].extend(all_errors)

    if args.json_output:
        out_path = Path(args.json_output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if report["ok"]:
        print(f"Validated {len(specs)} template(s) successfully.")
        return 0

    print("Validation failed:", file=sys.stderr)
    for err in report["errors"]:
        print(f"- {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
