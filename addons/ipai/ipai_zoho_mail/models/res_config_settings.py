# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ── SMTP ──────────────────────────────────────────────────────────────────

    zoho_smtp_host = fields.Char(
        string="SMTP Host",
        default="smtp.zoho.com",
        config_parameter="ipai_zoho_mail.smtp_host",
        help="Zoho Mail outgoing SMTP server hostname.",
    )

    zoho_smtp_port = fields.Integer(
        string="SMTP Port",
        default=587,
        config_parameter="ipai_zoho_mail.smtp_port",
        help="SMTP port (587 = STARTTLS, 465 = SSL/TLS).",
    )

    zoho_smtp_user = fields.Char(
        string="SMTP User (From)",
        config_parameter="ipai_zoho_mail.smtp_user",
        help="Email address used as the From address for outbound mail "
        "(e.g. notifications@insightpulseai.com).",
    )

    # ── IMAP ──────────────────────────────────────────────────────────────────

    zoho_imap_host = fields.Char(
        string="IMAP Host",
        default="imap.zoho.com",
        config_parameter="ipai_zoho_mail.imap_host",
        help="Zoho Mail incoming IMAP server hostname.",
    )

    zoho_imap_port = fields.Integer(
        string="IMAP Port",
        default=993,
        config_parameter="ipai_zoho_mail.imap_port",
        help="IMAP port (993 = SSL/TLS).",
    )

    zoho_imap_user = fields.Char(
        string="IMAP User (Catchall)",
        config_parameter="ipai_zoho_mail.imap_user",
        help="Email address to poll for incoming messages "
        "(e.g. catchall@insightpulseai.com).",
    )

    # ── Domain ────────────────────────────────────────────────────────────────

    zoho_from_domain = fields.Char(
        string="From Domain",
        default="@insightpulseai.com",
        config_parameter="ipai_zoho_mail.from_domain",
        help="Domain appended to Zoho Mail addresses (e.g. @insightpulseai.com).",
    )
