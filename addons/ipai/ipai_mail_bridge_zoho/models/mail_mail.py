# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import logging
import os

import requests
from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _bridge_url():
    return os.environ.get("ZOHO_MAIL_BRIDGE_URL", "").rstrip("/")


def _bridge_secret():
    # NOTE: This is a dedicated random shared secret (32+ chars).
    # It is NOT the Supabase anon key — that is a public client credential
    # and must NOT be used here. Generate with: openssl rand -hex 32
    return os.environ.get("ZOHO_MAIL_BRIDGE_SECRET", "")


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _ipai_bridge_enabled(self):
        """Return True if HTTPS bridge env vars are configured."""
        return bool(_bridge_url() and _bridge_secret())

    def _ipai_bridge_send_one(self, mail):
        """POST a single mail.mail record to the zoho-mail-bridge edge function.

        Bridge endpoint: POST {ZOHO_MAIL_BRIDGE_URL}?action=send_email
        Auth: x-bridge-secret: {ZOHO_MAIL_BRIDGE_SECRET}
              (dedicated shared secret — NOT the Supabase anon key)
        Payload: { from, to, subject, htmlBody?, textBody?, replyTo? }
        Response: { ok: true }
        """
        url = _bridge_url() + "?action=send_email"
        secret = _bridge_secret()

        to_list = [x.strip() for x in (mail.email_to or "").split(",") if x.strip()]
        if not to_list:
            raise UserError(_("No recipients (email_to) on mail id=%s") % mail.id)

        payload = {
            "from": mail.email_from,
            "to": ", ".join(to_list),
            "subject": mail.subject or "(no subject)",
        }

        if mail.body_html:
            payload["htmlBody"] = mail.body_html
        elif mail.body:
            payload["textBody"] = mail.body

        if mail.reply_to:
            payload["replyTo"] = mail.reply_to

        headers = {
            "Content-Type": "application/json",
            "x-bridge-secret": secret,
        }

        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
        except requests.exceptions.RequestException as exc:
            raise UserError(_("Zoho bridge connection error: %s") % exc) from exc

        if resp.status_code >= 300:
            raise UserError(_("Zoho bridge failed (HTTP %s): %s") % (resp.status_code, resp.text))

        return resp.json()

    def send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        """Override: route via HTTPS bridge if configured; else standard SMTP.

        This intercepts the mail.mail.send() business layer so the bridge
        is active for all send paths: cron queues, compose wizard, manual
        send, and programmatic env['mail.mail'].create(...).send() calls.

        Falls back to standard Odoo SMTP if ZOHO_MAIL_BRIDGE_URL or
        ZOHO_MAIL_BRIDGE_SECRET env vars are not set (safe for local dev).
        """
        if not self._ipai_bridge_enabled():
            return super().send(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                smtp_session=smtp_session,
            )

        for mail in self:
            try:
                result = self._ipai_bridge_send_one(mail)
                mail.write(
                    {
                        "state": "sent",
                        "failure_type": False,
                        "failure_reason": False,
                    }
                )
                _logger.info(
                    "ipai_mail_bridge_zoho: sent mail.mail id=%s via bridge ok=%s",
                    mail.id,
                    result.get("ok"),
                )
            except Exception as exc:
                _logger.exception("ipai_mail_bridge_zoho: failed to send mail.mail id=%s", mail.id)
                mail.write(
                    {
                        "state": "exception",
                        "failure_reason": str(exc),
                    }
                )
                if raise_exception:
                    raise

            if auto_commit:
                self.env.cr.commit()

        return True
