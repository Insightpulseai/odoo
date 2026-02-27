#!/usr/bin/env python3
"""
scripts/ci/check_industry_bundles.py
======================================
Gate script for ssot/odoo/industry_bundles.yaml.

Modes:
  (default) schema   -- Validate SSOT file structure only. CI-safe, no network.
  --mode audit       -- Compare ce_core + oca_replacements against live Odoo.
                        Requires ODOO_* env vars and SSH-accessible localhost:8069.

Exit codes:
  0 = all checks passed
  1 = schema error (missing key, invalid structure)
  2 = audit: required modules missing (ce_core or oca_replacements)
  3 = oca_extensions missing (warning only — audit mode with --strict-oca)

Usage:
  # Schema validation (CI gate — no Odoo connection required):
  python3 scripts/ci/check_industry_bundles.py

  # Audit a bundle against live Odoo:
  ODOO_URL=http://localhost:8069 ODOO_DB=odoo_prod \
  ODOO_ADMIN_LOGIN=admin ODOO_ADMIN_PASSWORD=<pw> \
  python3 scripts/ci/check_industry_bundles.py --mode audit --bundle photography

  # Audit with strict OCA extension check:
  python3 scripts/ci/check_industry_bundles.py --mode audit --bundle odoo-partner --strict-oca
"""
from __future__ import annotations

import argparse
import os
import sys
import xmlrpc.client
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not installed. Run: pip install pyyaml")

SSOT_FILE = Path(__file__).parent.parent.parent / "ssot" / "odoo" / "industry_bundles.yaml"
SCHEMA_EXPECTED = "ssot.odoo.industry_bundles.v1"

# ── Schema validation ─────────────────────────────────────────────────────────

REQUIRED_BUNDLE_KEYS = {"slug", "label", "odoo_industry_url", "ce_core", "oca_replacements"}
REQUIRED_MODULE_KEYS = {"name", "reason"}
REQUIRED_OCA_KEYS = {"name", "replaces_ee", "oca_repo", "reason"}


def validate_schema(data: dict) -> list[str]:
    """Return list of schema errors. Empty = valid."""
    errors: list[str] = []

    schema = data.get("schema")
    if schema != SCHEMA_EXPECTED:
        errors.append(f"schema: expected {SCHEMA_EXPECTED!r}, got {schema!r}")

    bundles = data.get("bundles")
    if not isinstance(bundles, list) or not bundles:
        errors.append("bundles: must be a non-empty list")
        return errors

    slugs_seen: set[str] = set()
    for i, bundle in enumerate(bundles):
        prefix = f"bundles[{i}]"

        # Required keys
        missing_keys = REQUIRED_BUNDLE_KEYS - set(bundle.keys())
        if missing_keys:
            errors.append(f"{prefix}: missing required keys: {sorted(missing_keys)}")

        slug = bundle.get("slug", f"<bundle-{i}>")

        # Duplicate slugs
        if slug in slugs_seen:
            errors.append(f"{prefix}: duplicate slug {slug!r}")
        slugs_seen.add(slug)

        # ce_core entries
        ce_core = bundle.get("ce_core", [])
        if not isinstance(ce_core, list) or not ce_core:
            errors.append(f"{prefix} ({slug}): ce_core must be a non-empty list")
        else:
            for j, mod in enumerate(ce_core):
                missing = REQUIRED_MODULE_KEYS - set(mod.keys())
                if missing:
                    errors.append(f"{prefix}.ce_core[{j}]: missing keys {sorted(missing)}")

        # oca_replacements entries
        oca_reps = bundle.get("oca_replacements", [])
        if not isinstance(oca_reps, list):
            errors.append(f"{prefix} ({slug}): oca_replacements must be a list")
        else:
            for j, mod in enumerate(oca_reps):
                missing = REQUIRED_OCA_KEYS - set(mod.keys())
                if missing:
                    errors.append(f"{prefix}.oca_replacements[{j}]: missing keys {sorted(missing)}")

        # oca_extensions — optional, but if present must have name + oca_repo
        oca_ext = bundle.get("oca_extensions", [])
        if not isinstance(oca_ext, list):
            errors.append(f"{prefix} ({slug}): oca_extensions must be a list if present")
        else:
            for j, mod in enumerate(oca_ext):
                if "name" not in mod or "oca_repo" not in mod:
                    errors.append(
                        f"{prefix}.oca_extensions[{j}]: must have 'name' and 'oca_repo'"
                    )

    return errors


# ── Live audit ────────────────────────────────────────────────────────────────

def _env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        sys.exit(f"ERROR: env var {key} is not set (required for --mode audit)")
    return val


def get_installed_modules(url: str, db: str, login: str, password: str) -> set[str]:
    """Return set of installed module names from ir.module.module."""
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, login, password, {})
    except Exception as exc:
        sys.exit(f"ERROR: cannot connect to {url}: {exc}")
    if not uid:
        sys.exit("ERROR: authentication failed")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    rows = models.execute_kw(
        db, uid, password,
        "ir.module.module", "search_read",
        [[[["state", "=", "installed"]]]],
        {"fields": ["name"], "limit": 0},
    )
    return {r["name"] for r in rows}


def audit_bundle(bundle: dict, installed: set[str], strict_oca: bool) -> tuple[list[str], list[str]]:
    """
    Returns (failures, warnings).
    failures: required ce_core + oca_replacements missing → exit 2
    warnings: oca_extensions missing → exit 3 with --strict-oca
    """
    failures: list[str] = []
    warnings: list[str] = []

    slug = bundle["slug"]

    for mod in bundle.get("ce_core", []):
        name = mod["name"]
        if name not in installed:
            failures.append(f"[{slug}] ce_core MISSING: {name!r} — {mod.get('reason', '')}")

    for mod in bundle.get("oca_replacements", []):
        name = mod["name"]
        if name not in installed:
            failures.append(
                f"[{slug}] oca_replacement MISSING: {name!r} "
                f"(replaces EE: {mod.get('replaces_ee', '?')}) — {mod.get('reason', '')}"
            )

    for mod in bundle.get("oca_extensions", []):
        name = mod["name"]
        if name not in installed:
            warnings.append(
                f"[{slug}] oca_extension absent: {name!r} — {mod.get('reason', '')}"
            )

    return failures, warnings


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate ssot/odoo/industry_bundles.yaml and optionally audit live Odoo"
    )
    ap.add_argument(
        "--mode",
        choices=["schema", "audit"],
        default="schema",
        help="'schema' (default) validates SSOT only. 'audit' checks live Odoo modules.",
    )
    ap.add_argument(
        "--bundle",
        help="Slug of the bundle to audit (required with --mode audit). Use 'all' for all bundles.",
    )
    ap.add_argument(
        "--strict-oca",
        action="store_true",
        help="Treat missing oca_extensions as failures (exit 3) in audit mode.",
    )
    args = ap.parse_args()

    # ── Load and validate schema ──────────────────────────────────────────────
    if not SSOT_FILE.exists():
        print(f"ERROR: SSOT file not found: {SSOT_FILE}", file=sys.stderr)
        return 1

    data = yaml.safe_load(SSOT_FILE.read_text()) or {}
    errors = validate_schema(data)

    if errors:
        print(f"SCHEMA ERRORS in {SSOT_FILE.name}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    bundles: list[dict] = data["bundles"]
    slug_map = {b["slug"]: b for b in bundles}

    print(f"OK: schema valid — {len(bundles)} bundle(s): {[b['slug'] for b in bundles]}")

    if args.mode == "schema":
        return 0

    # ── Audit mode ────────────────────────────────────────────────────────────
    if not args.bundle:
        print("ERROR: --bundle <slug|all> is required with --mode audit", file=sys.stderr)
        return 1

    if args.bundle == "all":
        target_bundles = bundles
    else:
        if args.bundle not in slug_map:
            print(
                f"ERROR: bundle {args.bundle!r} not found. "
                f"Available: {list(slug_map.keys())}",
                file=sys.stderr,
            )
            return 1
        target_bundles = [slug_map[args.bundle]]

    url = _env("ODOO_URL")
    db = _env("ODOO_DB")
    login = _env("ODOO_ADMIN_LOGIN")
    password = _env("ODOO_ADMIN_PASSWORD")

    print(f"Connecting to {url} db={db!r} ...")
    installed = get_installed_modules(url, db, login, password)
    print(f"  {len(installed)} modules installed")

    all_failures: list[str] = []
    all_warnings: list[str] = []

    for bundle in target_bundles:
        failures, warnings = audit_bundle(bundle, installed, args.strict_oca)
        all_failures.extend(failures)
        all_warnings.extend(warnings)

    if all_failures:
        print("\nFAILURES (required modules missing):", file=sys.stderr)
        for f in all_failures:
            print(f"  FAIL  {f}", file=sys.stderr)

    if all_warnings:
        label = "FAIL (--strict-oca)" if args.strict_oca else "WARN"
        print(f"\n{label} (optional OCA extensions not installed):")
        for w in all_warnings:
            print(f"  {label}  {w}")

    if all_failures:
        return 2

    if args.strict_oca and all_warnings:
        return 3

    if all_warnings:
        print("\nOK: all required modules present (optional extensions absent — warnings only)")
    else:
        print("\nOK: all required + optional modules present")

    return 0


if __name__ == "__main__":
    sys.exit(main())
