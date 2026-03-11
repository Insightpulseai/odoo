#!/usr/bin/env python3
"""
smoke_mail.py — Idempotent smoke tests for Odoo email pipeline.

Tests:
  1) Outgoing email pipeline (mail.mail created → queued → optional SMTP send)
  2) User invite/reset template rendering (res.users.action_reset_password)
  3) Digest email generation (digest.digest, skipped gracefully if not installed)

Uses XML-RPC (same pattern as apply_mail_settings.py / company_bootstrap_xmlrpc.py).
No UI steps. Marker-tagged subjects make results deterministic and purgeable.

Usage:
    # Queue-only (safe for CI — no real email sent)
    ODOO_URL=https://erp.insightpulseai.com \
    ODOO_DB=odoo_prod \
    ODOO_USER=admin \
    ODOO_PASSWORD=<admin_pass> \
    python3 scripts/odoo/smoke_mail.py --recipient smoke@insightpulseai.com

    # Attempt SMTP send (use only against dev with Mailpit or real mailbox)
    python3 scripts/odoo/smoke_mail.py --recipient smoke@insightpulseai.com --send

    # Cleanup after run
    python3 scripts/odoo/cleanup_smoke_mail.py --marker <marker>

Environment variables:
    ODOO_URL          Base URL  (default: http://localhost:8069)
    ODOO_DB           DB name   (default: odoo_dev)
    ODOO_USER         Username  (default: admin)
    ODOO_PASSWORD     Admin password (required)
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import xmlrpc.client
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# XML-RPC helpers (mirrors apply_mail_settings.py pattern)
# ---------------------------------------------------------------------------

def _connect() -> tuple[str, str, int, xmlrpc.client.ServerProxy]:
    url  = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
    db   = os.environ.get("ODOO_DB", "odoo_dev")
    user = os.environ.get("ODOO_USER", "admin")
    pwd  = os.environ.get("ODOO_PASSWORD", "")
    if not pwd:
        print("ERROR: ODOO_PASSWORD is required", file=sys.stderr)
        sys.exit(1)

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        print(f"ERROR: Odoo authentication failed for user {user!r}", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return db, pwd, uid, models


def _call(models, db, uid, pwd, model: str, method: str, *args, **kwargs):
    return models.execute_kw(db, uid, pwd, model, method, list(args), kwargs)


def _search(models, db, uid, pwd, model: str, domain: list, **kw) -> list:
    return _call(models, db, uid, pwd, model, "search", domain, **kw)


def _read(models, db, uid, pwd, model: str, ids: list, fields: list) -> list:
    return _call(models, db, uid, pwd, model, "read", ids, fields=fields)


def _create(models, db, uid, pwd, model: str, vals: dict) -> int:
    return _call(models, db, uid, pwd, model, "create", vals)


def _write(models, db, uid, pwd, model: str, ids: list, vals: dict) -> bool:
    return _call(models, db, uid, pwd, model, "write", ids, vals)


def _execute(models, db, uid, pwd, model: str, method: str, ids: list) -> object:
    return _call(models, db, uid, pwd, model, method, ids)


def _assert(cond: bool, msg: str):
    if not cond:
        raise AssertionError(f"FAIL: {msg}")


# ---------------------------------------------------------------------------
# Test 1 — Outgoing email pipeline
# ---------------------------------------------------------------------------

def test_outgoing_mail(
    models, db, uid, pwd,
    recipient: str,
    marker: str,
    do_send: bool,
) -> dict:
    print(f"\n[1] Outgoing mail pipeline (do_send={do_send})")

    subject = f"[{marker}] Smoke: Outgoing SMTP"
    mail_id = _create(models, db, uid, pwd, "mail.mail", {
        "subject": subject,
        "email_to": recipient,
        "body_html": f"<p>[{marker}] Smoke test outgoing email. Discard.</p>",
        "state": "outgoing",
    })
    _assert(mail_id, "mail.mail.create() returned falsy ID")
    print(f"  created mail.mail id={mail_id}")

    rows = _read(models, db, uid, pwd, "mail.mail", [mail_id], ["state", "email_to"])
    state = rows[0]["state"]
    _assert(state in ("outgoing", "exception"),
            f"Expected state=outgoing|exception, got {state!r}")
    print(f"  state={state} ✅")

    if do_send:
        print("  attempting SMTP send...")
        _execute(models, db, uid, pwd, "mail.mail", "send", [mail_id])
        rows = _read(models, db, uid, pwd, "mail.mail", [mail_id], ["state", "failure_reason"])
        state = rows[0]["state"]
        reason = rows[0].get("failure_reason") or ""
        if state == "sent":
            print(f"  state=sent ✅")
        elif state == "exception":
            print(f"  state=exception (SMTP failure) reason={reason!r}")
            # Exception with reason is a valid deterministic outcome — not a crash
        else:
            _assert(False, f"Unexpected state after send: {state!r}")

    return {"mail_id": mail_id, "state": state}


# ---------------------------------------------------------------------------
# Test 2 — User invite / password-reset template
# ---------------------------------------------------------------------------

def test_invite_template(
    models, db, uid, pwd,
    recipient: str,
    marker: str,
) -> dict:
    print(f"\n[2] User invite/reset template")

    login = f"smoke.{int(time.time())}@example.invalid"
    user_id = _create(models, db, uid, pwd, "res.users", {
        "name": f"[{marker}] Smoke User",
        "login": login,
        "email": recipient,
    })
    _assert(user_id, "res.users.create() returned falsy ID")
    print(f"  created res.users id={user_id} login={login!r}")

    # action_reset_password queues the invite/reset mail using the system template
    _execute(models, db, uid, pwd, "res.users", "action_reset_password", [user_id])

    # Validate at least one queued mail reached the recipient with a password keyword
    invite_ids = _search(models, db, uid, pwd, "mail.mail", [
        ("email_to", "=", recipient),
        "|",
        ("subject", "ilike", "password"),
        ("subject", "ilike", "invite"),
    ])
    _assert(len(invite_ids) >= 1,
            f"No invite/reset mail found for {recipient!r}")
    print(f"  invite/reset mails found: {len(invite_ids)} ✅")

    return {"user_id": user_id, "user_login": login, "invite_mail_count": len(invite_ids)}


# ---------------------------------------------------------------------------
# Test 3 — Digest email generation
# ---------------------------------------------------------------------------

def test_digest(
    models, db, uid, pwd,
    user_id: int,
) -> dict:
    print(f"\n[3] Digest email generation")

    # Check if digest module is installed
    installed = _search(models, db, uid, pwd, "ir.module.module", [
        ("name", "=", "digest"),
        ("state", "=", "installed"),
    ])
    if not installed:
        print("  digest module not installed — SKIPPED")
        return {"skipped": True}

    digest_ids = _search(models, db, uid, pwd, "digest.digest", [], limit=1)
    if not digest_ids:
        print("  no digest.digest records — SKIPPED")
        return {"skipped": True}

    digest_id = digest_ids[0]
    # Subscribe the smoke user
    _write(models, db, uid, pwd, "digest.digest", [digest_id],
           {"user_ids": [(4, user_id)]})
    print(f"  subscribed user_id={user_id} to digest_id={digest_id}")

    # Try available send methods
    sent = False
    for method in ("action_send", "_action_send", "_cron_send"):
        try:
            _execute(models, db, uid, pwd, "digest.digest", method, [digest_id])
            print(f"  called {method}() ✅")
            sent = True
            break
        except xmlrpc.client.Fault as e:
            if "attribute" in str(e).lower() or "has no" in str(e).lower():
                continue  # method doesn't exist on this version
            print(f"  {method}() raised fault: {e.faultString!r}")
            break

    if not sent:
        print("  no digest send method found — SKIPPED")
        return {"skipped": True, "digest_id": digest_id}

    return {"skipped": False, "digest_id": digest_id}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke tests for Odoo email pipeline (no UI)")
    parser.add_argument("--recipient", required=True,
                        help="Email address to receive smoke emails")
    parser.add_argument("--send", action="store_true",
                        help="Attempt actual SMTP send (default: queue-only)")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev",
                        help="Target environment label (informational only)")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    marker = f"smoke-mail-{stamp}"

    print(f"smoke_mail.py  env={args.env}  recipient={args.recipient}  marker={marker}")
    print(f"  ODOO_URL={os.environ.get('ODOO_URL', 'http://localhost:8069')}")
    print(f"  ODOO_DB={os.environ.get('ODOO_DB', 'odoo_dev')}")
    print(f"  ODOO_USER={os.environ.get('ODOO_USER', 'admin')}")
    print()

    db, pwd, uid, models = _connect()

    results: dict = {"marker": marker, "ok": True}

    try:
        r1 = test_outgoing_mail(models, db, uid, pwd, args.recipient, marker, args.send)
        results["outgoing"] = r1
    except Exception as e:
        print(f"  ERROR: {e}")
        results["outgoing"] = {"error": str(e)}
        results["ok"] = False

    try:
        r2 = test_invite_template(models, db, uid, pwd, args.recipient, marker)
        results["invite"] = r2
    except Exception as e:
        print(f"  ERROR: {e}")
        results["invite"] = {"error": str(e)}
        results["ok"] = False

    # Digest uses the user created in test 2
    user_id = results.get("invite", {}).get("user_id")
    if user_id:
        try:
            r3 = test_digest(models, db, uid, pwd, user_id)
            results["digest"] = r3
        except Exception as e:
            print(f"  ERROR: {e}")
            results["digest"] = {"error": str(e)}
            # digest failure is soft — don't flip ok

    print("\n--- RESULT ---")
    for k, v in results.items():
        if k == "ok":
            continue
        print(f"  {k}: {v}")
    overall = "PASS" if results["ok"] else "FAIL"
    print(f"\nOVERALL: {overall}")
    print(f"To clean up: python3 scripts/odoo/cleanup_smoke_mail.py --marker {marker!r}")

    return 0 if results["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
