#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
E2E test for Odoo built-in user invitation email (auth_signup.set_password_email).

Tests that Odoo's invite flow — generate signup token → send set_password_email
template — routes through the configured outgoing mail server and delivers.

Run INSIDE the Odoo container:

    docker cp scripts/mail/e2e_odoo_invite.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/e2e_odoo_invite.py

Exits:
    0 — invite mail.mail.state='sent'
    1 — invite mail.mail.state='exception'
    2 — timed out waiting for terminal state
    3 — unexpected error / template not found

Environment:
    ODOO_DB      — database name (default: odoo_prod)
    INVITE_EMAIL — recipient address for test invite (default: test-invite@insightpulseai.com)
    DB_PASSWORD  — optional, overrides ${DB_PASSWORD} template in odoo.conf
    KEEP_USER    — set to "1" to skip cleanup of the created test user (default: delete)

Strategy:
    1. Create a fresh internal user with INVITE_EMAIL (inactive, no password).
    2. Call user.action_reset_password() — uses auth_signup.set_password_email.
    3. Poll mail.mail for the sent invite (filter by email_to + template subject).
    4. Clean up the test user (unless KEEP_USER=1).
    5. Emit single-line JSON PASS/EXCEPTION/TIMEOUT/ERROR.
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("e2e_odoo_invite")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
INVITE_EMAIL = os.environ.get("INVITE_EMAIL", "test-invite@insightpulseai.com")
KEEP_USER = os.environ.get("KEEP_USER", "0") == "1"
POLL_TIMEOUT = 60   # seconds
POLL_INTERVAL = 5   # seconds

TEMPLATE_XMLID = "auth_signup.set_password_email"


def _emit(status, mail_id=None, server=None, to=None, reason=None, template=None):
    """Print a single-line JSON result for CI/health-check consumers."""
    print(json.dumps({
        "status": status,   # PASS | EXCEPTION | TIMEOUT | ERROR
        "mail_id": mail_id,
        "server": server,
        "to": to or INVITE_EMAIL,
        "template": template or TEMPLATE_XMLID,
        "reason": reason,
        "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }), flush=True)


def main():
    try:
        import odoo.tools.config
        db_password = os.environ.get("DB_PASSWORD", "")
        parse_args = ["--config=/etc/odoo/odoo.conf"]
        if db_password:
            parse_args.append(f"--db_password={db_password}")
        odoo.tools.config.parse_config(parse_args)
        from odoo.modules.registry import Registry
        from odoo import api

        registry = Registry(ODOO_DB)
    except Exception as exc:
        _logger.error("Failed to initialise Odoo registry: %s", exc)
        _emit("ERROR", reason=str(exc))
        return 3

    user_id = None
    created_user = False

    try:
        # ── Step 1: Verify template exists ────────────────────────────────
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})
            try:
                tmpl = env.ref(TEMPLATE_XMLID)
                _logger.info("Template found: %r (id=%d)", tmpl.name, tmpl.id)
            except Exception:
                _logger.error("Template %r not found — is auth_signup installed?", TEMPLATE_XMLID)
                _emit("ERROR", reason=f"template {TEMPLATE_XMLID!r} not found")
                return 3

        # ── Step 2: Create (or find) test user ────────────────────────────
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})

            existing = env["res.users"].search(
                [("login", "=", INVITE_EMAIL)], limit=1
            )
            if existing:
                user_id = existing.id
                created_user = False
                _logger.info(
                    "Re-using existing user id=%d login=%r", user_id, INVITE_EMAIL
                )
            else:
                user = env["res.users"].with_context(no_reset_password=True).create({
                    "name": "E2E Invite Test User",
                    "login": INVITE_EMAIL,
                    "email": INVITE_EMAIL,
                    "groups_id": [(6, 0, [
                        env.ref("base.group_user").id,
                    ])],
                })
                user_id = user.id
                created_user = True
                _logger.info(
                    "Created test user id=%d login=%r", user_id, INVITE_EMAIL
                )
            cr.commit()

        # ── Step 3: Trigger invite (action_reset_password) ────────────────
        created_before = None
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})
            created_before = time.time()
            user = env["res.users"].browse(user_id)
            user.action_reset_password()
            cr.commit()
            _logger.info(
                "action_reset_password() called — polling mail.mail (up to %ds)…",
                POLL_TIMEOUT,
            )

        # ── Step 4: Poll for the invite mail ──────────────────────────────
        mail_id = None
        state = "outgoing"
        reason = ""
        deadline = time.time() + POLL_TIMEOUT

        while time.time() < deadline:
            time.sleep(POLL_INTERVAL)
            with registry.cursor() as cr:
                env = api.Environment(cr, 1, {})
                # Find the most recent mail to INVITE_EMAIL created after our trigger
                mails = env["mail.mail"].search(
                    [
                        ("email_to", "like", INVITE_EMAIL),
                        ("create_date", ">=",
                         time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.gmtime(created_before - 5))),
                    ],
                    order="id desc",
                    limit=1,
                )
                if mails:
                    mail_id = mails.id
                    state = mails.state
                    reason = mails.failure_reason or ""

            _logger.info(
                "  mail_id=%s  state=%r  failure_reason=%r", mail_id, state, reason
            )

            if mail_id and state == "sent":
                _logger.info(
                    "✅ PASS — invite delivered (mail.mail id=%d)", mail_id
                )
                _emit("PASS", mail_id=mail_id, to=INVITE_EMAIL)
                return 0
            if mail_id and state == "exception":
                _logger.error("❌ EXCEPTION (id=%d): %s", mail_id, reason)
                _emit("EXCEPTION", mail_id=mail_id, reason=reason)
                return 1

        _logger.error(
            "⏱  Timed out after %ds — mail_id=%s last state=%r",
            POLL_TIMEOUT, mail_id, state,
        )
        _emit("TIMEOUT", mail_id=mail_id, reason=f"last_state={state}")
        return 2

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        _emit("ERROR", reason=str(exc))
        return 3

    finally:
        # ── Step 5: Clean up test user ────────────────────────────────────
        if created_user and not KEEP_USER and user_id:
            try:
                with registry.cursor() as cr:
                    env = api.Environment(cr, 1, {})
                    user = env["res.users"].browse(user_id)
                    user.toggle_active()   # archive (never hard-delete users)
                    cr.commit()
                    _logger.info("Archived test user id=%d", user_id)
            except Exception as ex:
                _logger.warning("Could not archive test user id=%d: %s", user_id, ex)


if __name__ == "__main__":
    sys.exit(main())
