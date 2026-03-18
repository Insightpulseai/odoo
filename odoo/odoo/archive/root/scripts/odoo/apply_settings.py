#!/usr/bin/env python3
"""
scripts/odoo/apply_settings.py
================================
Idempotent XML-RPC applier for config/odoo/settings.yaml.

Usage:
    python scripts/odoo/apply_settings.py [--dry-run] [--env prod|dev]

Env vars required:
    ODOO_URL          e.g. https://erp.insightpulseai.com
    ODOO_DB           e.g. odoo_prod
    ODOO_ADMIN_LOGIN  e.g. admin
    ODOO_ADMIN_PASSWORD

Exit codes:
    0 = all settings applied (or dry-run passed)
    1 = error (auth, connection, bad key)
    2 = dry-run diff detected (changes would be made)
"""
from __future__ import annotations

import argparse
import os
import sys
import xmlrpc.client
from pathlib import Path

import yaml

SETTINGS_FILE = Path(__file__).parent.parent / "config" / "odoo" / "settings.yaml"

# Keys that MUST NOT be applied via this script (owned by other appliers)
BLOCKED_KEYS = {
    # Mail settings — use apply_mail_settings.py
    "mail.catchall.domain",
    "mail.default.from",
    "mail.server",
    # Secrets — never in config parameters
    "auth_signup.reset_password_token",
}

_TRUTHY = {"true", "1", "yes"}
_FALSY = {"false", "0", "no"}


def _norm(value: str) -> str:
    """Normalise True/False casing for Odoo bool config params."""
    if value.lower() in _TRUTHY:
        return "True"
    if value.lower() in _FALSY:
        return "False"
    return value


def load_settings(env: str) -> dict[str, str]:
    data = yaml.safe_load(SETTINGS_FILE.read_text())
    params: dict[str, str] = {}
    for k, v in (data.get("config_parameters") or {}).items():
        if k not in BLOCKED_KEYS:
            params[k] = _norm(str(v))
    return params


def connect(url: str, db: str, login: str, password: str):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, login, password, {})
    if not uid:
        print("ERROR: Odoo auth failed", file=sys.stderr)
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models


def get_existing(models, uid, db, password, keys: list[str]) -> dict[str, str]:
    records = models.execute_kw(
        db, uid, password,
        "ir.config_parameter", "search_read",
        [[["key", "in", keys]]],
        {"fields": ["key", "value"]},
    )
    return {r["key"]: r["value"] for r in records}


def apply(
    models, uid, db: str, password: str,
    desired: dict[str, str],
    dry_run: bool = False,
) -> int:
    existing = get_existing(models, uid, db, password, list(desired.keys()))
    changed = 0

    for key, want in desired.items():
        have = existing.get(key, "<NOT SET>")
        if have == want:
            continue

        changed += 1
        marker = "[DRY-RUN]" if dry_run else "[APPLY]"
        print(f"{marker} {key}: {have!r} → {want!r}")

        if not dry_run:
            models.execute_kw(
                db, uid, password,
                "ir.config_parameter", "set_param",
                [key, want],
            )

    if changed == 0:
        print("✓ All settings already match SSOT. No changes.")
    elif not dry_run:
        print(f"✓ Applied {changed} parameter(s).")
    else:
        print(f"→ Dry run: {changed} parameter(s) would change.")

    return changed


def verify(models, uid, db: str, password: str, desired: dict[str, str]) -> bool:
    existing = get_existing(models, uid, db, password, list(desired.keys()))
    ok = True
    for key, want in desired.items():
        have = existing.get(key, "<NOT SET>")
        if have != want:
            print(f"FAIL  {key}: expected={want!r} actual={have!r}", file=sys.stderr)
            ok = False
    if ok:
        print("✓ Verification passed.")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply Odoo settings SSOT")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--env", default="prod", choices=["prod", "dev"])
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    url = os.environ.get("ODOO_URL", "").rstrip("/")
    db = os.environ.get("ODOO_DB", "")
    login = os.environ.get("ODOO_ADMIN_LOGIN", "admin")
    password = os.environ.get("ODOO_ADMIN_PASSWORD", "")

    for name, val in [("ODOO_URL", url), ("ODOO_DB", db), ("ODOO_ADMIN_PASSWORD", password)]:
        if not val:
            print(f"ERROR: {name} is required", file=sys.stderr)
            sys.exit(1)

    desired = load_settings(args.env)
    print(f"Settings file: {SETTINGS_FILE}")
    print(f"Target: {url}  db={db}  keys={len(desired)}")

    uid, models = connect(url, db, login, password)

    if args.verify_only:
        ok = verify(models, uid, db, password, desired)
        sys.exit(0 if ok else 1)

    changed = apply(models, uid, db, password, desired, dry_run=args.dry_run)

    if args.dry_run:
        sys.exit(2 if changed else 0)

    # Post-apply verification
    ok = verify(models, uid, db, password, desired)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
