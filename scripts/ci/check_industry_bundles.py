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
  3 = audit: required extension missing (oca_extensions with optional=false, --strict-oca only)

Usage:
  # Schema validation (CI gate — no Odoo connection required):
  python3 scripts/ci/check_industry_bundles.py

  # Audit a bundle against live Odoo:
  ODOO_URL=http://localhost:8069 ODOO_DB=odoo_prod \\
  ODOO_ADMIN_LOGIN=admin ODOO_ADMIN_PASSWORD=<pw> \\
  python3 scripts/ci/check_industry_bundles.py --mode audit --bundle photography

  # Audit all bundles with strict OCA extension check (optional=false fails):
  python3 scripts/ci/check_industry_bundles.py --mode audit --bundle all --strict-oca
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
REQUIRED_EXT_KEYS = {"addon", "repo", "optional", "rationale"}


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
        slug = bundle.get("slug", f"<bundle-{i}>")

        # Required keys
        missing_keys = REQUIRED_BUNDLE_KEYS - set(bundle.keys())
        if missing_keys:
            errors.append(f"{prefix} ({slug}): missing required keys: {sorted(missing_keys)}")

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

        # oca_extensions — optional list; if present each entry must have all REQUIRED_EXT_KEYS
        # and optional field must be a bool.
        oca_ext = bundle.get("oca_extensions", [])
        if not isinstance(oca_ext, list):
            errors.append(f"{prefix} ({slug}): oca_extensions must be a list if present")
        else:
            for j, mod in enumerate(oca_ext):
                if not isinstance(mod, dict):
                    errors.append(f"{prefix}.oca_extensions[{j}]: must be a mapping, got {type(mod).__name__}")
                    continue
                missing = REQUIRED_EXT_KEYS - set(mod.keys())
                if missing:
                    errors.append(
                        f"{prefix}.oca_extensions[{j}]: missing keys {sorted(missing)} "
                        f"(required: addon, repo, optional, rationale)"
                    )
                if "optional" in mod and not isinstance(mod["optional"], bool):
                    errors.append(
                        f"{prefix}.oca_extensions[{j}] ({mod.get('addon', '?')}): "
                        f"'optional' must be a bool, got {type(mod['optional']).__name__!r}"
                    )

        # ee_modules — optional list of strings
        ee_mods = bundle.get("ee_modules", [])
        if not isinstance(ee_mods, list):
            errors.append(f"{prefix} ({slug}): ee_modules must be a list if present")
        else:
            for j, m in enumerate(ee_mods):
                if not isinstance(m, str):
                    errors.append(f"{prefix}.ee_modules[{j}]: must be a string")

        # notes — optional list of strings
        notes = bundle.get("notes", [])
        if not isinstance(notes, list):
            errors.append(f"{prefix} ({slug}): notes must be a list if present")

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


class AuditResult:
    """Categorized audit findings for one bundle."""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        self.missing_ce_core: list[str] = []
        self.missing_oca_replacements: list[str] = []
        self.missing_required_extensions: list[str] = []   # optional=false, strict-oca
        self.missing_optional_extensions: list[str] = []   # optional=true, warn only

    @property
    def has_failures(self) -> bool:
        return bool(self.missing_ce_core or self.missing_oca_replacements)

    @property
    def has_strict_failures(self) -> bool:
        return bool(self.missing_required_extensions)

    @property
    def has_warnings(self) -> bool:
        return bool(self.missing_optional_extensions)

    def print_report(self, strict_oca: bool) -> None:
        slug = self.slug
        any_issue = (
            self.missing_ce_core
            or self.missing_oca_replacements
            or (strict_oca and self.missing_required_extensions)
            or self.missing_optional_extensions
        )
        if not any_issue:
            print(f"  [{slug}] OK — all required modules present")
            if not self.missing_optional_extensions:
                print(f"  [{slug}] OK — all optional extensions present")
            return

        if self.missing_ce_core:
            print(f"  [{slug}] FAIL ce_core missing ({len(self.missing_ce_core)}):")
            for m in self.missing_ce_core:
                print(f"           install: {m}")

        if self.missing_oca_replacements:
            print(f"  [{slug}] FAIL oca_replacement missing ({len(self.missing_oca_replacements)}):")
            for m in self.missing_oca_replacements:
                print(f"           install: {m}")

        if self.missing_required_extensions:
            label = "FAIL" if strict_oca else "WARN"
            print(
                f"  [{slug}] {label} required_extension missing "
                f"({len(self.missing_required_extensions)}):"
            )
            for m in self.missing_required_extensions:
                print(f"           install: {m}")

        if self.missing_optional_extensions:
            print(
                f"  [{slug}] WARN optional_extension absent "
                f"({len(self.missing_optional_extensions)}) — skippable:"
            )
            for m in self.missing_optional_extensions:
                print(f"           optional: {m}")


def audit_bundle(bundle: dict, installed: set[str]) -> AuditResult:
    result = AuditResult(bundle["slug"])

    for mod in bundle.get("ce_core", []):
        if mod["name"] not in installed:
            result.missing_ce_core.append(mod["name"])

    for mod in bundle.get("oca_replacements", []):
        if mod["name"] not in installed:
            result.missing_oca_replacements.append(mod["name"])

    for ext in bundle.get("oca_extensions", []):
        addon = ext["addon"]
        if addon not in installed:
            if ext.get("optional", True):
                result.missing_optional_extensions.append(addon)
            else:
                result.missing_required_extensions.append(addon)

    return result


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
        help="Slug to audit (required with --mode audit). Use 'all' for all bundles.",
    )
    ap.add_argument(
        "--strict-oca",
        action="store_true",
        help="Treat oca_extensions with optional=false as required failures (exit 3).",
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
    print(f"  {len(installed)} modules installed\n")

    results = [audit_bundle(b, installed) for b in target_bundles]

    print("── Audit results ─────────────────────────────────────────────────────")
    for r in results:
        r.print_report(args.strict_oca)

    # ── Remediation summary ───────────────────────────────────────────────────
    all_required_missing = sorted(
        set(
            m
            for r in results
            for m in (r.missing_ce_core + r.missing_oca_replacements)
        )
    )
    all_strict_missing = sorted(
        set(m for r in results for m in r.missing_required_extensions)
    ) if args.strict_oca else []

    if all_required_missing or all_strict_missing:
        print("\n── Remediation (install these) ───────────────────────────────────────")
        for m in all_required_missing:
            print(f"  odoo -i {m} --stop-after-init")
        if all_strict_missing:
            print(f"  # (--strict-oca required extensions)")
            for m in all_strict_missing:
                print(f"  odoo -i {m} --stop-after-init")

    # ── Final verdict ─────────────────────────────────────────────────────────
    has_failures = any(r.has_failures for r in results)
    has_strict = args.strict_oca and any(r.has_strict_failures for r in results)

    if has_failures:
        return 2
    if has_strict:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
