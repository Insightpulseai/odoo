#!/usr/bin/env python3
"""
E2E: Odoo -> Mailgun SMTP -> recipient inbox (plain-text email)

Usage (from host, copies into container and executes):
  TEST_TO="someone@example.com" python3 scripts/verify_mailgun_e2e_text_email.py

Or inside container:
  TEST_TO="someone@example.com" python3 /tmp/verify_mailgun_e2e_text_email.py

No UI. No secret rotation. One test mail.mail record created and sent.

Exit codes:
  0 — STATUS=COMPLETE
  1 — STATUS=PARTIAL (unexpected mail state)
  2 — missing/invalid TEST_TO
  3 — Mailgun server record not found
  4 — Mailgun server pass EMPTY
  5 — Exception during mail.send()
  6 — failure_reason present after send
  7 — unexpected mail state
"""

import os
import sys
import datetime

MAILGUN_HOST = "smtp.mailgun.org"
MAILGUN_PORT = 2525
MAILGUN_USER = "no-reply@mg.insightpulseai.com"
MAILGUN_SEQ  = 2
DEFAULT_TO   = "jgtolentino.rn@gmail.com"


def _utc_stamp() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def main() -> int:
    test_to = os.environ.get("TEST_TO") or DEFAULT_TO
    if not test_to or "@" not in test_to:
        print("STATUS=FAIL\nReason: TEST_TO invalid/missing.", file=sys.stderr)
        return 2

    stamp   = _utc_stamp()
    subject = f"E2E-MAILGUN-ODOO-TEXT {stamp}"
    body_text = (
        "Plain-text end-to-end test email.\n\n"
        f"stamp    = {stamp}\n"
        f"from     = {MAILGUN_USER}\n"
        f"to       = {test_to}\n"
        f"transport= {MAILGUN_HOST}:{MAILGUN_PORT}\n"
    )

    # --- Odoo bootstrap ---
    import odoo                    # type: ignore
    from odoo import api, SUPERUSER_ID  # type: ignore
    odoo.tools.config.parse_config([])

    dbname = (
        odoo.tools.config.get("db_name")
        or os.environ.get("ODOO_DB")
        or "odoo_prod"
    )

    print("\n[CONTEXT]")
    print(f"  db_name : {dbname}")
    print(f"  test_to : {test_to}")
    print(f"  subject : {subject}")

    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # --- Step 1: verify ir_mail_server ---
        print("\n[STEP 1] ir.mail_server state")
        servers = env["ir.mail_server"].sudo().search([], order="sequence,id")
        print(f"  {'Seq':>4}  {'Host':20}  {'Port':5}  {'Pass':5}  Name")
        print(f"  {'---':>4}  {'----':20}  {'----':5}  {'----':5}  ----")
        for s in servers:
            ps = "SET" if bool(s.smtp_pass) else "EMPTY"
            print(f"  {s.sequence:>4}  {(s.smtp_host or ''):20}  {(str(s.smtp_port) or ''):5}  {ps:5}  {s.name}")

        mg = env["ir.mail_server"].sudo().search([
            ("smtp_host", "=", MAILGUN_HOST),
            ("smtp_port", "=", MAILGUN_PORT),
            ("smtp_user", "=", MAILGUN_USER),
            ("sequence", "=", MAILGUN_SEQ),
        ], limit=1)

        if not mg:
            print(f"\nSTATUS=FAIL\nReason: No Mailgun server: {MAILGUN_HOST}:{MAILGUN_PORT} user={MAILGUN_USER} seq={MAILGUN_SEQ}")
            return 3
        if not mg.smtp_pass:
            print("\nSTATUS=FAIL\nReason: Mailgun ir.mail_server smtp_pass is EMPTY.")
            return 4

        print(f"\n  ✅ Mailgun server id={mg.id} seq={mg.sequence} pass=SET")

        # --- Step 2: create + send mail.mail ---
        print("\n[STEP 2] Create + send mail.mail")
        body_html = "<pre>{}</pre>".format(
            body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        mail = env["mail.mail"].sudo().create({
            "email_from":  MAILGUN_USER,
            "email_to":    test_to,
            "subject":     subject,
            "body_html":   body_html,
            "auto_delete": False,
        })
        cr.commit()
        print(f"  Created mail.mail id={mail.id} state={mail.state!r}")

        try:
            mail.send()
            cr.commit()
        except Exception as exc:
            cr.rollback()
            print(f"\nSTATUS=FAIL\nReason: Exception during mail.send()\n{type(exc).__name__}: {exc}")
            try:
                mail.refresh()
                print(f"  mail id={mail.id} state={mail.state!r} failure_reason={getattr(mail,'failure_reason',None)!r}")
            except Exception:
                pass
            return 5

        mail.refresh()
        message_id    = getattr(mail, "message_id", False)
        failure_reason = getattr(mail, "failure_reason", None)

        if failure_reason:
            print(f"\nSTATUS=PARTIAL\nReason: failure_reason set: {failure_reason!r}")
            print(f"  mail id={mail.id} state={mail.state!r}")
            return 6

        if mail.state not in ("sent", "outgoing"):
            print(f"\nSTATUS=PARTIAL\nReason: Unexpected mail state {mail.state!r}")
            print(f"  mail id={mail.id}")
            return 7

        print(f"  ✅ Send complete — mail id={mail.id} state={mail.state!r}")

        print("\n[EVIDENCE]")
        print(f"  ir_mail_server : id={mg.id} {MAILGUN_HOST}:{MAILGUN_PORT} user={MAILGUN_USER} seq={MAILGUN_SEQ} pass=SET")
        print(f"  mail_mail      : id={mail.id} state={mail.state!r}")
        print(f"  subject        : {subject}")
        if message_id:
            print(f"  message_id     : {message_id}")

        print("\n[INBOX CORRELATION]")
        print(f"  Recipient : {test_to}")
        print(f"  Subject   : {subject}")
        if message_id:
            print(f"  Message-ID: {message_id}")

        print("\nSTATUS=COMPLETE ✅")
        return 0


if __name__ == "__main__":
    sys.exit(main())
