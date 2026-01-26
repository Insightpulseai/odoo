# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAssetCategory(models.Model):
    """Asset category for grouping assets with common depreciation settings."""

    _name = "account.asset.category"
    _description = "Asset Category"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain="[('type', '=', 'general')]",
    )
    account_asset_id = fields.Many2one(
        "account.account",
        string="Asset Account",
        required=True,
        domain="[('account_type', '=', 'asset_fixed')]",
    )
    account_depreciation_id = fields.Many2one(
        "account.account",
        string="Depreciation Account",
        required=True,
        help="Account for accumulated depreciation",
    )
    account_expense_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        required=True,
        help="Account for depreciation expense",
    )

    # Default Depreciation Settings
    method = fields.Selection(
        [
            ("linear", "Straight Line"),
            ("degressive", "Declining Balance"),
        ],
        default="linear",
        required=True,
    )
    method_number = fields.Integer(
        string="Number of Depreciations",
        default=5,
    )
    method_period = fields.Selection(
        [
            ("1", "Monthly"),
            ("3", "Quarterly"),
            ("12", "Yearly"),
        ],
        default="12",
    )
    prorata = fields.Boolean(string="Prorata Temporis")
