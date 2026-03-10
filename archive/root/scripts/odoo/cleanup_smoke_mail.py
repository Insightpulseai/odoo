#!/usr/bin/env python3
"""
cleanup_smoke_mail.py — Purge smoke test artifacts from Odoo.

Deletes:
  - mail.mail rows whose subject contains the marker string
  - res.users created by smoke_mail.py (login contains "smoke.")

Usage:
    python3 scripts/odoo/cleanup_smoke_mail.py --marker "smoke-mail-20260221T123456Z"

Environment variables: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD
"""
from __future__ import annotations
import argparse, os, sys, xmlrpc.client


def _connect():
    url  = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
    db   = os.environ.get("ODOO_DB", "odoo_dev")
    user = os.environ.get("ODOO_USER", "admin")
    pwd  = os.environ.get("ODOO_PASSWORD", "")
    if not pwd:
        print("ERROR: ODOO_PASSWORD required", file=sys.stderr); sys.exit(1)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        print("ERROR: auth failed", file=sys.stderr); sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return db, pwd, uid, models


def _call(m, db, uid, pwd, model, method, *args, **kw):
    return m.execute_kw(db, uid, pwd, model, method, list(args), kw)


def main() -> int:
    p = argparse.ArgumentParser(description="Clean up smoke_mail.py artifacts")
    p.add_argument("--marker", required=True,
                   help="Marker string used in smoke run (e.g. smoke-mail-20260221T123456Z)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    db, pwd, uid, models = _connect()

    # mail.mail cleanup
    mail_ids = _call(models, db, uid, pwd, "mail.mail", "search",
                     [[("subject", "ilike", args.marker)]])
    print(f"mail.mail rows matching marker: {len(mail_ids)}")
    if mail_ids and not args.dry_run:
        _call(models, db, uid, pwd, "mail.mail", "unlink", mail_ids)
        print(f"  deleted {len(mail_ids)} mail.mail rows")

    # res.users cleanup (smoke users have login containing "smoke.")
    user_ids = _call(models, db, uid, pwd, "res.users", "search",
                     [[("login", "like", "smoke."),
                       ("name", "ilike", args.marker)]])
    print(f"res.users smoke rows: {len(user_ids)}")
    if user_ids and not args.dry_run:
        _call(models, db, uid, pwd, "res.users", "unlink", user_ids)
        print(f"  deleted {len(user_ids)} res.users rows")

    if args.dry_run:
        print("[dry-run] no changes applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
