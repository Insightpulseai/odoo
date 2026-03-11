#!/usr/bin/env python3
"""
scripts/odoo/apply_website_theme.py
=====================================
Idempotently apply website theme based on ssot/website/theme.yaml.

Strategy: XML-RPC via localhost:8069 executed over SSH.
Port 8069 is firewalled externally; run this script FROM the server
or pipe through SSH (default behaviour when ODOO_URL is localhost).

Usage (from CI / local with SSH access):
    python scripts/odoo/apply_website_theme.py [--dry-run] [--env prod]

Env vars required:
    ODOO_URL           e.g. http://localhost:8069   (use over SSH)
    ODOO_DB            e.g. odoo_prod
    ODOO_ADMIN_LOGIN   e.g. admin
    ODOO_ADMIN_PASSWORD

SSH wrapper (recommended for prod):
    ssh root@178.128.112.214 \
      "ODOO_URL=http://localhost:8069 ODOO_DB=odoo_prod \
       ODOO_ADMIN_LOGIN=admin ODOO_ADMIN_PASSWORD=<pw> \
       python3 /opt/odoo/repo/scripts/odoo/apply_website_theme.py --env prod"

Exit codes:
    0 = theme already correct (no-op) or successfully applied
    1 = error (auth, connection, module not installed)
    2 = dry-run diff detected (would make changes)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import xmlrpc.client
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not installed. Run: pip install pyyaml")

SSOT_FILE = Path(__file__).parent.parent.parent / "ssot" / "website" / "theme.yaml"
SCHEMA_EXPECTED = "ssot.website.theme.v1"


# ── helpers ──────────────────────────────────────────────────────────────────

def _env(key: str, required: bool = True) -> str:
    val = os.environ.get(key, "")
    if required and not val:
        sys.exit(f"ERROR: env var {key} is not set")
    return val


def _load_ssot(env_name: str) -> dict:
    if not SSOT_FILE.exists():
        sys.exit(f"ERROR: SSOT file not found: {SSOT_FILE}")
    data = yaml.safe_load(SSOT_FILE.read_text()) or {}
    schema = data.get("schema")
    if schema != SCHEMA_EXPECTED:
        sys.exit(f"ERROR: unexpected schema {schema!r} in {SSOT_FILE}")
    targets = data.get("targets") or []
    for t in targets:
        if t.get("env") == env_name:
            return t
    sys.exit(f"ERROR: no target with env={env_name!r} in {SSOT_FILE}")


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Idempotently apply website theme from SSOT")
    ap.add_argument("--env", default="prod", help="Target env name in ssot/website/theme.yaml")
    ap.add_argument("--dry-run", action="store_true", help="Report diff without writing")
    args = ap.parse_args()

    target = _load_ssot(args.env)
    ssot_module  = target["theme_module"]
    ssot_wid     = int(target["website_id"])
    ssot_hint_id = target.get("theme_id")

    url      = _env("ODOO_URL")
    db       = _env("ODOO_DB")
    login    = _env("ODOO_ADMIN_LOGIN")
    password = _env("ODOO_ADMIN_PASSWORD")

    # ── auth ──────────────────────────────────────────────────────────────
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, login, password, {})
    except Exception as exc:
        sys.exit(f"ERROR: cannot connect to {url}: {exc}")
    if not uid:
        sys.exit("ERROR: authentication failed — check ODOO_ADMIN_LOGIN / ODOO_ADMIN_PASSWORD")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

    def rpc(model, method, *args, **kwargs):
        return models.execute_kw(db, uid, password, model, method, *args, **kwargs)

    # ── resolve theme module ───────────────────────────────────────────────
    mods = rpc("ir.module.module", "search_read",
               [[["name", "=", ssot_module]]],
               {"fields": ["id", "name", "state"], "limit": 1})
    if not mods:
        sys.exit(f"ERROR: module {ssot_module!r} not found in ir.module.module")
    mod = mods[0]
    if mod["state"] != "installed":
        sys.exit(
            f"ERROR: module {ssot_module!r} is not installed (state={mod['state']!r}). "
            f"Run: odoo -i {ssot_module} --stop-after-init"
        )
    theme_mod_id = mod["id"]

    # ── resolve current website state ─────────────────────────────────────
    websites = rpc("website", "search_read",
                   [[["id", "=", ssot_wid]]],
                   {"fields": ["id", "name", "theme_id"], "limit": 1})
    if not websites:
        sys.exit(f"ERROR: website id={ssot_wid} not found")
    website = websites[0]
    current_theme = website.get("theme_id")  # False or [id, name]
    current_id = current_theme[0] if current_theme else None

    # ── diff ──────────────────────────────────────────────────────────────
    # The target is theme_mod_id (ir.module.module id).
    # website.theme_id IS a Many2one to ir.module.module in Odoo CE 19.
    already_correct = (current_id == theme_mod_id)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[{stamp}] website_id={ssot_wid} name={website['name']!r}")
    print(f"  module   : {ssot_module!r} (id={theme_mod_id}, state={mod['state']})")
    print(f"  current  : theme_id={current_id} ({current_theme[1] if current_theme else 'none'})")
    print(f"  target   : theme_id={theme_mod_id} ({ssot_module})")

    if already_correct:
        print("  STATUS   : no-op (already correct)")
        return 0

    if args.dry_run:
        print("  STATUS   : DIFF — would set theme_id →", theme_mod_id)
        return 2

    # ── apply ─────────────────────────────────────────────────────────────
    rpc("website", "write", [[ssot_wid], {"theme_id": theme_mod_id}])

    # ── verify write ──────────────────────────────────────────────────────
    after = rpc("website", "search_read",
                [[["id", "=", ssot_wid]]],
                {"fields": ["id", "theme_id"], "limit": 1})
    after_id = after[0]["theme_id"][0] if after[0].get("theme_id") else None
    if after_id != theme_mod_id:
        sys.exit(f"ERROR: write did not take effect — theme_id is {after_id} after write")

    print(f"  STATUS   : APPLIED — theme_id set to {theme_mod_id}")

    # ── evidence artifact ─────────────────────────────────────────────────
    evidence_dir = Path(__file__).parent.parent.parent / "docs" / "evidence" / "odoo"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"theme_apply_{stamp}.json"
    evidence = {
        "stamp": stamp,
        "env": args.env,
        "ssot_file": str(SSOT_FILE.relative_to(Path(__file__).parent.parent.parent)),
        "module": {"id": theme_mod_id, "name": ssot_module, "state": mod["state"]},
        "before": {
            "website_id": ssot_wid,
            "website_name": website["name"],
            "theme_id": current_id,
            "theme_name": current_theme[1] if current_theme else None,
        },
        "after": {
            "website_id": ssot_wid,
            "theme_id": after_id,
        },
        "changed": True,
    }
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"  EVIDENCE : {evidence_path.relative_to(Path(__file__).parent.parent.parent)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
