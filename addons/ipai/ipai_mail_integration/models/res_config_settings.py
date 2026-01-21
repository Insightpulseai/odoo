# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Mail Integration Settings
    ipai_mail_google_enabled = fields.Boolean(
        string="Enable Gmail Integration",
        config_parameter="ipai_mail.google_enabled",
        help="Enable direct Gmail API integration (replaces EE mail_plugin_gmail)",
    )
    ipai_mail_google_client_id = fields.Char(
        string="Google Client ID",
        config_parameter="ipai_mail.google_client_id",
    )

    ipai_mail_microsoft_enabled = fields.Boolean(
        string="Enable Outlook Integration",
        config_parameter="ipai_mail.microsoft_enabled",
        help="Enable direct MS Graph integration (replaces EE mail_plugin_outlook)",
    )
    ipai_mail_microsoft_client_id = fields.Char(
        string="Microsoft Client ID",
        config_parameter="ipai_mail.microsoft_client_id",
    )
    ipai_mail_microsoft_tenant_id = fields.Char(
        string="Microsoft Tenant ID",
        config_parameter="ipai_mail.microsoft_tenant_id",
        help="Use 'common' for multi-tenant apps",
    )

    # Mass Mailing Provider
    ipai_mass_mailing_provider = fields.Selection(
        [
            ("smtp", "SMTP (Any Provider)"),
            ("mailgun", "Mailgun API"),
            ("ses", "AWS SES API"),
            ("sendgrid", "SendGrid API"),
        ],
        string="Mass Mailing Provider",
        config_parameter="ipai_mail.mass_mailing_provider",
        default="smtp",
        help="Email service provider for mass mailings (replaces IAP)",
    )
    ipai_mailgun_api_key = fields.Char(
        string="Mailgun API Key",
        config_parameter="ipai_mail.mailgun_api_key",
    )
    ipai_mailgun_domain = fields.Char(
        string="Mailgun Domain",
        config_parameter="ipai_mail.mailgun_domain",
    )
