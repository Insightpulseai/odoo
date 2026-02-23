# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    ipai_mailgun_last_event = fields.Char(
        string="Last Mailgun Event",
        help="Most recent event reported by Mailgun (delivered, opened, clicked, bounced, etc.)",
    )
