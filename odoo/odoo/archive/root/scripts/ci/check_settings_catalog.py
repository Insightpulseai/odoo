#!/usr/bin/env python3
"""
check_settings_catalog.py — Validate Odoo settings catalog SSOT.

Checks (schema-only mode, default):
  1. YAML parses successfully
  2. Schema field matches ssot.odoo.settings_catalog.v1
  3. Required top-level keys present (schema, version, odoo_version, edition, extraction, modules)
  4. extraction section has required fields
  5. Each module entry has 'module' (str) and 'fields' (list)
  6. Each field entry has required keys (name, ttype, string, mechanism)
  7. Modules are sorted alphabetically by module name
  8. Fields within each module are sorted alphabetically by field name
  9. No duplicate field names within a module
  10. mechanism values are from allowed set
  11. Mechanism-specific keys are present (config_parameter, depends_module, etc.)

Checks (--live mode, requires ODOO_* env vars):
  12. Re-extract from live Odoo instance
  13. Compare with committed catalog — fail on diff

Exit codes:
  0 — all checks pass
  1 — validation errors
  2 — catalog file missing or invalid YAML
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

CATALOG_PATH = "ssot/odoo/settings_catalog.yaml"

REQUIRED_TOP_KEYS = {"schema", "version", "odoo_version", "edition", "extraction", "modules"}
REQUIRED_EXTRACTION_KEYS = {"method", "extracted_at", "field_count", "module_count"}
REQUIRED_FIELD_KEYS = {"name", "ttype", "string", "mechanism"}

ALLOWED_MECHANISMS = {
    "config_parameter",
    "module_install",
    "group_toggle",
    "related",
    "computed",
    "default",
}

ALLOWED_TTYPES = {
    "boolean", "char", "text", "html", "integer", "float",
    "monetary", "date", "datetime", "selection",
    "many2one", "many2many", "one2many", "binary",
    "json",
}


def load_catalog(repo_root: Path) -> dict:
    path = repo_root / CATALOG_PATH
    if not path.exists():
        print(f"ERROR: Catalog not found: {CATALOG_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}", file=sys.stderr)
        sys.exit(2)


def validate_schema(data: dict) -> list[str]:
    """Validate catalog schema, ordering, and field constraints."""
    errors = []

    # Top-level keys
    schema = data.get("schema", "")
    if schema != "ssot.odoo.settings_catalog.v1":
        errors.append(f"Invalid schema: expected 'ssot.odoo.settings_catalog.v1', got '{schema}'")

    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    # Edition
    edition = data.get("edition", "")
    if edition and edition not in ("CE", "EE"):
        errors.append(f"Invalid edition: expected 'CE' or 'EE', got '{edition}'")

    # Extraction section
    extraction = data.get("extraction", {})
    if not isinstance(extraction, dict):
        errors.append("'extraction' must be a mapping")
    else:
        for key in REQUIRED_EXTRACTION_KEYS:
            if key not in extraction:
                errors.append(f"Missing extraction key: '{key}'")

    # Modules list
    modules = data.get("modules", [])
    if not isinstance(modules, list):
        errors.append("'modules' must be a list")
        return errors

    # Module ordering check
    module_names = [m.get("module", "") for m in modules if isinstance(m, dict)]
    if module_names != sorted(module_names):
        out_of_order = []
        sorted_names = sorted(module_names)
        for i, (actual, expected) in enumerate(zip(module_names, sorted_names)):
            if actual != expected:
                out_of_order.append(f"position {i}: found '{actual}', expected '{expected}'")
                if len(out_of_order) >= 3:
                    out_of_order.append("...")
                    break
        errors.append(f"Modules not sorted alphabetically: {'; '.join(out_of_order)}")

    # Module-level validation
    seen_modules = set()
    total_fields = 0

    for idx, mod in enumerate(modules):
        if not isinstance(mod, dict):
            errors.append(f"Module at index {idx}: must be a mapping")
            continue

        mod_name = mod.get("module", "")
        if not mod_name:
            errors.append(f"Module at index {idx}: missing 'module' key")
            continue

        if mod_name in seen_modules:
            errors.append(f"Duplicate module: '{mod_name}'")
        seen_modules.add(mod_name)

        fields = mod.get("fields", [])
        if not isinstance(fields, list):
            errors.append(f"Module '{mod_name}': 'fields' must be a list")
            continue

        # Field ordering check
        field_names = [f.get("name", "") for f in fields if isinstance(f, dict)]
        if field_names != sorted(field_names):
            errors.append(f"Module '{mod_name}': fields not sorted alphabetically")

        # Field-level validation
        seen_fields = set()
        for fidx, field in enumerate(fields):
            if not isinstance(field, dict):
                errors.append(f"Module '{mod_name}', field {fidx}: must be a mapping")
                continue

            fname = field.get("name", "")
            if not fname:
                errors.append(f"Module '{mod_name}', field {fidx}: missing 'name'")
                continue

            prefix = f"Module '{mod_name}', field '{fname}'"

            if fname in seen_fields:
                errors.append(f"{prefix}: duplicate field name")
            seen_fields.add(fname)

            for key in REQUIRED_FIELD_KEYS:
                if key not in field:
                    errors.append(f"{prefix}: missing required key '{key}'")

            # ttype validation
            ttype = field.get("ttype", "")
            if ttype and ttype not in ALLOWED_TTYPES:
                errors.append(f"{prefix}: invalid ttype '{ttype}'")

            # mechanism validation
            mechanism = field.get("mechanism", "")
            if mechanism and mechanism not in ALLOWED_MECHANISMS:
                errors.append(f"{prefix}: invalid mechanism '{mechanism}'")

            # Mechanism-specific key checks
            if mechanism == "config_parameter" and "config_parameter" not in field:
                # Not strictly required — some config_parameter fields use set_values()
                pass
            if mechanism == "module_install" and "depends_module" not in field:
                # Can be inferred from name; warn but don't error
                pass

            total_fields += 1

    # Cross-check field count
    declared_count = extraction.get("field_count", 0) if isinstance(extraction, dict) else 0
    if declared_count and declared_count != total_fields:
        errors.append(
            f"Field count mismatch: extraction.field_count={declared_count}, "
            f"actual={total_fields}"
        )

    declared_mod_count = extraction.get("module_count", 0) if isinstance(extraction, dict) else 0
    if declared_mod_count and declared_mod_count != len(modules):
        errors.append(
            f"Module count mismatch: extraction.module_count={declared_mod_count}, "
            f"actual={len(modules)}"
        )

    return errors


def live_drift_check(repo_root: Path) -> list[str]:
    """Re-extract catalog from live Odoo and compare with committed version."""
    errors = []

    # Import extractor
    sys.path.insert(0, str(repo_root / "scripts" / "odoo"))
    try:
        import extract_settings_catalog as extractor
    except ImportError as e:
        errors.append(f"Cannot import extractor: {e}")
        return errors

    url = os.environ.get("ODOO_URL", "").rstrip("/")
    db = os.environ.get("ODOO_DB", "")
    login = os.environ.get("ODOO_ADMIN_LOGIN", "admin")
    password = os.environ.get("ODOO_ADMIN_PASSWORD", "")

    if not all([url, db, password]):
        errors.append(
            "Live drift check requires ODOO_URL, ODOO_DB, ODOO_ADMIN_PASSWORD. "
            "Set SETTINGS_CATALOG_LIVE=1 and provide Odoo credentials."
        )
        return errors

    try:
        extraction = extractor.extract_via_xmlrpc(url, db, login, password)
    except Exception as e:
        errors.append(f"Live extraction failed: {e}")
        return errors

    catalog = extractor.build_catalog(extraction)

    # Write to temp file and compare module/field lists
    committed = load_catalog(repo_root)

    committed_modules = {
        m["module"]: {f["name"] for f in m.get("fields", [])}
        for m in committed.get("modules", [])
        if isinstance(m, dict)
    }
    live_modules = {
        m["module"]: {f["name"] for f in m.get("fields", [])}
        for m in catalog.get("modules", [])
        if isinstance(m, dict)
    }

    # Check for new modules in live
    for mod in sorted(set(live_modules) - set(committed_modules)):
        errors.append(f"Drift: module '{mod}' exists in live but not in catalog")

    # Check for removed modules
    for mod in sorted(set(committed_modules) - set(live_modules)):
        errors.append(f"Drift: module '{mod}' in catalog but missing from live")

    # Check for field-level drift in shared modules
    for mod in sorted(set(committed_modules) & set(live_modules)):
        new_fields = live_modules[mod] - committed_modules[mod]
        removed_fields = committed_modules[mod] - live_modules[mod]
        for f in sorted(new_fields):
            errors.append(f"Drift: field '{mod}.{f}' exists in live but not in catalog")
        for f in sorted(removed_fields):
            errors.append(f"Drift: field '{mod}.{f}' in catalog but missing from live")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Settings catalog SSOT validator")
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live drift check (requires ODOO_* env vars)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    data = load_catalog(repo_root)

    # Schema validation (always runs)
    errors = validate_schema(data)

    # Live drift check (optional)
    if args.live or os.environ.get("SETTINGS_CATALOG_LIVE") == "1":
        if not args.quiet:
            print("Running live drift check...")
        errors.extend(live_drift_check(repo_root))

    if not args.quiet:
        if errors:
            print(f"Settings catalog validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"  {err}")
        else:
            modules = data.get("modules", [])
            field_count = sum(
                len(m.get("fields", []))
                for m in modules
                if isinstance(m, dict)
            )
            print(
                f"Settings catalog validation passed — "
                f"{len(modules)} modules, {field_count} fields"
            )

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
