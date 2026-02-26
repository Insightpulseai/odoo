# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Override ir.mail_server to add Zoho Mail API transport.

When a mail server record has ``use_zoho_api=True``, outbound email is sent
via ZohoMailClient instead of SMTP.  This fully bypasses DigitalOcean's SMTP
block on ports 25/465/587.

Priority rules (lowest sequence = highest priority in Odoo):
- If mail_server_id is specified and that server has use_zoho_api=True → Zoho API
- If no mail_server_id, and a Zoho API server exists → Zoho API (seq=1 default)
- Otherwise → standard SMTP via super()
"""

import logging
from email.header import decode_header as _decode_header_raw

from odoo import api, fields, models
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


# ── Email message parsing helpers ─────────────────────────────────────────────


def _decode_header(value):
    """Return a decoded string from an RFC 2047 email header."""
    if not value:
        return ""
    parts = []
    for raw, charset in _decode_header_raw(value):
        if isinstance(raw, bytes):
            parts.append(raw.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(raw)
    return "".join(parts)


def _split_addresses(value):
    """Return list of non-empty stripped addresses from a comma-joined header."""
    if not value:
        return []
    return [a.strip() for a in value.split(",") if a.strip()]


def _extract_body(message):
    """Walk MIME parts; return (html_body, text_body).  Both may be None."""
    html_body = None
    text_body = None

    if message.is_multipart():
        for part in message.walk():
            ct = part.get_content_type()
            if ct == "text/html" and html_body is None:
                raw = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                html_body = raw.decode(charset, errors="replace")
            elif ct == "text/plain" and text_body is None:
                raw = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                text_body = raw.decode(charset, errors="replace")
    else:
        raw = message.get_payload(decode=True)
        if raw:
            charset = message.get_content_charset() or "utf-8"
            if message.get_content_type() == "text/html":
                html_body = raw.decode(charset, errors="replace")
            else:
                text_body = raw.decode(charset, errors="replace")

    return html_body, text_body


# ── Model ─────────────────────────────────────────────────────────────────────


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    use_zoho_api = fields.Boolean(
        string="Send via Zoho Mail API",
        default=False,
        help=(
            "Route outbound email through Zoho Mail REST API (HTTPS port 443) "
            "instead of SMTP.  Bypasses DigitalOcean SMTP port block.\n\n"
            "Requires Zoho OAuth credentials stored in ir.config_parameter:\n"
            "  ipai.zoho.client_id\n"
            "  ipai.zoho.client_secret\n"
            "  ipai.zoho.refresh_token\n"
            "  ipai.zoho.account_id\n\n"
            "Run scripts/setup_zoho_mail_api.sh to set these."
        ),
    )

    # ── Internal: find a Zoho-API-enabled server ──────────────────────────────

    def _zoho_server_for(self, mail_server_id=None):
        """Return the ir.mail_server record to use for Zoho API, or None.

        If mail_server_id is given → use that server if it has use_zoho_api=True.
        If mail_server_id is None  → pick highest-priority Zoho API server (seq ASC).
        """
        if mail_server_id:
            server = self.sudo().browse(mail_server_id)
            return server if server.use_zoho_api else None
        return self.sudo().search(
            [("use_zoho_api", "=", True), ("active", "=", True)],
            order="sequence asc",
            limit=1,
        ) or None

    # ── Override _connect__ (Odoo 19) ────────────────────────────────────────

    def _connect__(  # noqa: PLW3201
        self,
        host=None,
        port=None,
        user=None,
        password=None,
        encryption=None,
        smtp_from=None,
        ssl_certificate=None,
        ssl_private_key=None,
        smtp_debug=False,
        mail_server_id=None,
        allow_archived=False,
    ):
        """Skip SMTP connect for Zoho API servers (send_email handles the REST call).

        Odoo 19's mail.mail.send() calls _connect__() before send_email().
        Attempting an actual SMTP connection to mail.zoho.com:465 would block/
        timeout on DigitalOcean (SMTP ports 25/465/587 are blocked).
        Return None so send_email() proceeds directly to our REST API path.
        """
        server = self._zoho_server_for(mail_server_id)
        if server:
            _logger.debug(
                "ipai_zoho_mail_api: skipping SMTP connect for Zoho API server '%s' "
                "(will use HTTPS REST API instead)",
                server.name,
            )
            return None  # No SMTP session needed; send_email() uses Zoho REST API
        return super()._connect__(
            host=host,
            port=port,
            user=user,
            password=password,
            encryption=encryption,
            smtp_from=smtp_from,
            ssl_certificate=ssl_certificate,
            ssl_private_key=ssl_private_key,
            smtp_debug=smtp_debug,
            mail_server_id=mail_server_id,
            allow_archived=allow_archived,
        )

    # ── Override send_email ───────────────────────────────────────────────────

    @api.model
    def send_email(
        self,
        message,
        mail_server_id=None,
        smtp_server=None,
        smtp_port=False,
        smtp_user=None,
        smtp_password=None,
        smtp_encryption="none",
        smtp_ssl_certificate=None,
        smtp_ssl_private_key=None,
        smtp_debug=False,
        smtp_session=None,
    ):
        """Send ``message`` via Zoho API if applicable, else standard SMTP."""
        server = self._zoho_server_for(mail_server_id)
        if not server:
            return super().send_email(
                message,
                mail_server_id=mail_server_id,
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                smtp_encryption=smtp_encryption,
                smtp_ssl_certificate=smtp_ssl_certificate,
                smtp_ssl_private_key=smtp_ssl_private_key,
                smtp_debug=smtp_debug,
                smtp_session=smtp_session,
            )

        # ── Route via Zoho Mail API ──────────────────────────────────────────
        try:
            from ..services.zoho_client import ZohoMailClient

            client = ZohoMailClient(self.env)

            from_addr = _decode_header(message.get("From", ""))
            to_addrs = _split_addresses(message.get("To", ""))
            cc_addrs = _split_addresses(message.get("Cc", ""))
            bcc_addrs = _split_addresses(message.get("Bcc", ""))
            subject = _decode_header(message.get("Subject", "(no subject)"))
            reply_to = _decode_header(message.get("Reply-To", "")) or None
            html_body, text_body = _extract_body(message)

            if not to_addrs:
                raise MailDeliveryException(
                    "No recipients (To:) found in message; cannot send."
                )

            client.send_message(
                from_addr=from_addr,
                to_addrs=to_addrs,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                cc_addrs=cc_addrs or None,
                bcc_addrs=bcc_addrs or None,
                reply_to=reply_to,
            )

            # Return Message-Id so Odoo can record it on mail.mail.
            return message.get("Message-Id") or "<zoho-sent@insightpulseai.com>"

        except MailDeliveryException:
            raise
        except Exception as exc:
            _logger.exception("ipai_zoho_mail_api: send_email failed")
            raise MailDeliveryException(
                f"Zoho Mail API delivery failed: {exc}"
            ) from exc
