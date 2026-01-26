# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    """Extends account move with asset reference."""

    _inherit = "account.move"

    asset_depreciation_ids = fields.One2many(
        "account.asset.depreciation.line",
        "move_id",
        string="Depreciation Lines",
        readonly=True,
    )
