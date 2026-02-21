#!/usr/bin/env python3
"""
scripts/odoo/apply_auth_providers.py
======================================
Idempotent XML-RPC applier for config/odoo/auth_providers.yaml.

Manages Odoo auth.oauth.provider records.
Enforces the allowlist: any enabled provider not in SSOT is flagged.
Disables forbidden providers if found.

Usage:
    python scripts/odoo/apply_auth_providers.py [--dry-run] [--enforce]

Env vars required:
    ODOO_URL, ODOO_DB, ODOO_ADMIN_LOGIN, ODOO_ADMIN_PASSWORD

Exit codes:
    0 = all providers applied / already correct
    1 = error
    2 = dry-run diff detected
    3 = violation found (unexpected provider enabled, --enforce mode)
"""
from __future__ import annotations

import argparse
import os
import sys
import xmlrpc.client
from pathlib import Path

import yaml

CONFIG_FILE = Path(__file__).parent.parent / "config" / "odoo" / "auth_providers.yaml"

# Odoo model for OAuth providers (auth_oauth module)
PROVIDER_MODEL = "auth.oauth.provider"

# Fields we manage (introspect on first run to validate against actual schema)
MANAGED_FIELDS = [
    "name", "enabled", "auth_link", "body", "css_class", "sequence",
    "client_id", "scope", "validation_endpoint",
]


def _env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        print(f"ERROR: env var {key} is required but not set", file=sys.stderr)
        sys.exit(1)
    return val


def connect():
    url = os.environ.get("ODOO_URL", "").rstrip("/")
    db = os.environ.get("ODOO_DB", "")
    login = os.environ.get("ODOO_ADMIN_LOGIN", "admin")
    password = os.environ.get("ODOO_ADMIN_PASSWORD", "")
    for n, v in [("ODOO_URL", url), ("ODOO_DB", db), ("ODOO_ADMIN_PASSWORD", password)]:
        if not v:
            print(f"ERROR: {n} is required", file=sys.stderr)
            sys.exit(1)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, login, password, {})
    if not uid:
        print("ERROR: Odoo auth failed", file=sys.stderr)
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models, db, password


def get_existing_providers(models, uid, db, password) -> list[dict]:
    return models.execute_kw(
        db, uid, password, PROVIDER_MODEL, "search_read",
        [[]],
        {"fields": ["id", "name", "enabled", "client_id"]},
    )


def validate_schema(models, uid, db, password) -> None:
    """Fail fast if auth.oauth.provider doesn't exist (module not installed)."""
    try:
        fields = models.execute_kw(
            db, uid, password, PROVIDER_MODEL, "fields_get",
            [], {"attributes": ["string", "type"]},
        )
        if "name" not in fields:
            print(f"ERROR: {PROVIDER_MODEL} has no 'name' field — module not installed?",
                  file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"ERROR: cannot introspect {PROVIDER_MODEL}: {exc}", file=sys.stderr)
        sys.exit(1)


def apply_providers(
    models, uid, db, password,
    providers: list[dict],
    dry_run: bool,
) -> int:
    existing = {p["name"]: p for p in get_existing_providers(models, uid, db, password)}
    changed = 0

    for p in providers:
        name = p["name"]
        # Resolve env-var references for client credentials
        client_id = os.environ.get(p.get("client_id_env", ""), "")
        # Build the desired record
        desired = {
            "name": name,
            "enabled": p.get("enabled", True),
            "body": p.get("body", name),
            "css_class": p.get("css_class", ""),
            "sequence": p.get("sequence", 10),
            "scope": p.get("scopes", "openid profile email"),
            # auth_link is the authorize endpoint for auth_oauth
            "auth_link": p.get("auth_endpoint", ""),
            "validation_endpoint": p.get("userinfo_endpoint", ""),
        }
        if client_id:
            desired["client_id"] = client_id

        if name in existing:
            record = existing[name]
            marker = "[DRY-RUN]" if dry_run else "[UPDATE]"
            changed += 1
            print(f"{marker} Update provider: {name} (id={record['id']})")
            if not dry_run:
                models.execute_kw(
                    db, uid, password, PROVIDER_MODEL, "write",
                    [[record["id"]], desired],
                )
        else:
            changed += 1
            marker = "[DRY-RUN]" if dry_run else "[CREATE]"
            print(f"{marker} Create provider: {name}")
            if not dry_run:
                models.execute_kw(
                    db, uid, password, PROVIDER_MODEL, "create",
                    [desired],
                )

    return changed


def enforce_allowlist(
    models, uid, db, password,
    allowlist: list[str],
    forbidden: list[str],
    dry_run: bool,
) -> int:
    existing = get_existing_providers(models, uid, db, password)
    violations = 0

    for p in existing:
        if p["name"] in forbidden and p.get("enabled"):
            violations += 1
            print(f"VIOLATION: forbidden provider '{p['name']}' is enabled (id={p['id']})")
            if not dry_run:
                models.execute_kw(
                    db, uid, password, PROVIDER_MODEL, "write",
                    [[p["id"]], {"enabled": False}],
                )
                print(f"  → Disabled.")
        elif p["name"] not in allowlist and p.get("enabled"):
            violations += 1
            print(f"WARN: provider '{p['name']}' is enabled but not in allowlist")

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply Odoo OAuth provider SSOT")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--enforce", action="store_true",
                        help="Disable forbidden providers and flag allowlist violations")
    args = parser.parse_args()

    cfg = yaml.safe_load(CONFIG_FILE.read_text())
    providers: list[dict] = cfg.get("providers", [])
    allowlist: list[str] = cfg.get("allowlist", [p["name"] for p in providers])
    forbidden: list[str] = cfg.get("forbidden", [])

    uid, models, db, password = connect()
    validate_schema(models, uid, db, password)

    print(f"Config: {CONFIG_FILE}")
    print(f"Providers to apply: {[p['name'] for p in providers]}")

    changed = apply_providers(models, uid, db, password, providers, args.dry_run)

    if args.enforce:
        violations = enforce_allowlist(
            models, uid, db, password, allowlist, forbidden, args.dry_run
        )
        if violations:
            sys.exit(3)

    if changed == 0:
        print("✓ All providers already match SSOT.")
    elif args.dry_run:
        print(f"→ Dry run: {changed} provider(s) would change.")
        sys.exit(2)
    else:
        print(f"✓ Applied {changed} provider(s).")


if __name__ == "__main__":
    main()
