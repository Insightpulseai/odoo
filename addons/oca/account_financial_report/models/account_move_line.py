# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    """Extends account move line for financial reporting."""

    _inherit = "account.move.line"

    report_partner_id = fields.Many2one(
        related="partner_id",
        string="Report Partner",
        store=True,
    )
    report_account_group_id = fields.Many2one(
        related="account_id.group_id",
        string="Account Group",
        store=True,
    )
