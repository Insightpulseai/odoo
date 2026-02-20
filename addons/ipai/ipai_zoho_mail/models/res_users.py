# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    zoho_mail_id = fields.Char(
        string="Zoho Mail Address",
        help="Personal Zoho Mail address for this user (e.g. john@insightpulseai.com). "
        "Used to associate user messages with a specific Zoho inbox.",
    )
