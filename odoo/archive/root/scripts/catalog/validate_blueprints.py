#!/usr/bin/env python3
"""
validate_blueprints.py
──────────────────────
Validate all *.blueprint.yaml files in docs/catalog/blueprints/.

Exit codes:
  0  All blueprints valid
  1  Validation error — see output
  2  Usage / system error (missing pyyaml etc.)

Usage:
  python3 scripts/catalog/validate_blueprints.py
  python3 scripts/catalog/validate_blueprints.py --verbose
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).parent.parent.parent
BLUEPRINT_DIR = REPO_ROOT / "docs" / "catalog" / "blueprints"

REQUIRED_TOP_KEYS = {"id", "title", "category", "sources", "target", "variables", "automation", "verification", "rollback"}
ALLOWED_CATEGORIES = {"ops-console", "odoo-runtime", "observability", "platform-kit", "ai-ops-agent", "multi-tenant", "marketing"}
ALLOWED_SOURCE_TYPES = {"vercel-example", "vercel-template", "supabase-example", "supabase-ui", "supabase-platform-kit", "doc"}
ALLOWED_ROLLBACK_STRATEGIES = {"revert_pr", "delete_files", "restore_backup", "manual"}
ALLOWED_PKG_MANAGERS = {"pnpm", "npm", "yarn"}

VERBOSE = "--verbose" in sys.argv


def err(msg: str) -> None:
    print(f"  ERROR: {msg}", file=sys.stderr)


def validate_blueprint(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"Invalid YAML: {e}"]

    if not isinstance(data, dict):
        return ["Blueprint must be a YAML mapping"]

    # Required top-level keys
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")
        return errors

    # id matches filename
    file_id = path.stem.replace(".blueprint", "")
    bp_id = data.get("id", "")
    if bp_id != file_id:
        errors.append(f"id '{bp_id}' does not match filename stem '{file_id}'")

    # category
    if data.get("category") not in ALLOWED_CATEGORIES:
        errors.append(f"category must be one of {sorted(ALLOWED_CATEGORIES)}, got '{data.get('category')}'")

    # sources
    sources = data.get("sources", [])
    if not isinstance(sources, list) or len(sources) == 0:
        errors.append("sources must be a non-empty list")
    else:
        for i, src in enumerate(sources):
            if src.get("type") not in ALLOWED_SOURCE_TYPES:
                errors.append(f"sources[{i}].type must be one of {sorted(ALLOWED_SOURCE_TYPES)}, got '{src.get('type')}'")
            if not src.get("url"):
                errors.append(f"sources[{i}]: url is required")

    # target
    target = data.get("target", {})
    if not target.get("app_dir"):
        errors.append("target.app_dir is required")
    if "package_manager" in target and target["package_manager"] not in ALLOWED_PKG_MANAGERS:
        errors.append(f"target.package_manager must be one of {sorted(ALLOWED_PKG_MANAGERS)}")

    # variables
    variables = data.get("variables", [])
    if not isinstance(variables, list):
        errors.append("variables must be a list")
    else:
        for i, var in enumerate(variables):
            if not var.get("name"):
                errors.append(f"variables[{i}]: name is required")
            if "required" not in var:
                errors.append(f"variables[{i}]: required field is missing")

    # automation.steps
    automation = data.get("automation", {})
    steps = automation.get("steps", [])
    if not isinstance(steps, list) or len(steps) == 0:
        errors.append("automation.steps must be a non-empty list")
    else:
        for i, step in enumerate(steps):
            if not step.get("name"):
                errors.append(f"automation.steps[{i}]: name is required")
            if not step.get("description") and not step.get("agent_instruction"):
                errors.append(f"automation.steps[{i}]: description or agent_instruction is required")

    # verification.required_checks
    verification = data.get("verification", {})
    checks = verification.get("required_checks", [])
    if not isinstance(checks, list) or len(checks) == 0:
        errors.append("verification.required_checks must be a non-empty list")

    # rollback
    rollback = data.get("rollback", {})
    if rollback.get("strategy") not in ALLOWED_ROLLBACK_STRATEGIES:
        errors.append(f"rollback.strategy must be one of {sorted(ALLOWED_ROLLBACK_STRATEGIES)}")

    # notes.minor_customization must exist
    notes = data.get("notes", {})
    if not notes.get("minor_customization"):
        errors.append("notes.minor_customization is required (list the manual steps)")

    return errors


def main() -> int:
    blueprint_files = sorted(BLUEPRINT_DIR.glob("*.blueprint.yaml"))
    if not blueprint_files:
        print(f"ERROR: No *.blueprint.yaml files found in {BLUEPRINT_DIR}", file=sys.stderr)
        return 2

    total_errors = 0
    for path in blueprint_files:
        rel = path.relative_to(REPO_ROOT)
        errors = validate_blueprint(path)
        if errors:
            print(f"\n❌ {rel} ({len(errors)} error(s)):")
            for e in errors:
                err(e)
            total_errors += len(errors)
        else:
            print(f"✅ {rel}")

    if total_errors > 0:
        print(f"\n{total_errors} validation error(s) found.", file=sys.stderr)
        return 1

    print(f"\nAll {len(blueprint_files)} blueprint(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
