# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    """Fixed Asset with depreciation tracking."""

    _name = "account.asset"
    _description = "Fixed Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(string="Reference", copy=False)
    category_id = fields.Many2one(
        "account.asset.category",
        string="Asset Category",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Running"),
            ("close", "Close"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Financial Fields
    original_value = fields.Monetary(
        string="Gross Value",
        required=True,
        tracking=True,
    )
    salvage_value = fields.Monetary(
        string="Salvage Value",
        help="Residual value at end of useful life",
    )
    book_value = fields.Monetary(
        string="Book Value",
        compute="_compute_book_value",
        store=True,
    )
    accumulated_depreciation = fields.Monetary(
        compute="_compute_book_value",
        store=True,
    )

    # Depreciation Configuration
    method = fields.Selection(
        [
            ("linear", "Straight Line"),
            ("degressive", "Declining Balance"),
            ("degressive_then_linear", "Declining then Straight Line"),
        ],
        default="linear",
        required=True,
    )
    method_number = fields.Integer(
        string="Number of Depreciations",
        default=5,
        required=True,
    )
    method_period = fields.Selection(
        [
            ("1", "Monthly"),
            ("3", "Quarterly"),
            ("12", "Yearly"),
        ],
        default="12",
        required=True,
    )
    prorata = fields.Boolean(
        string="Prorata Temporis",
        help="First depreciation entry based on actual start date",
    )

    # Dates
    date_start = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.today,
    )
    date_end = fields.Date(
        string="End Date",
        compute="_compute_date_end",
        store=True,
    )

    # Depreciation Lines
    depreciation_line_ids = fields.One2many(
        "account.asset.depreciation.line",
        "asset_id",
        string="Depreciation Lines",
    )

    # Accounting
    account_asset_id = fields.Many2one(
        "account.account",
        string="Asset Account",
        related="category_id.account_asset_id",
        readonly=True,
    )
    account_depreciation_id = fields.Many2one(
        "account.account",
        string="Depreciation Account",
        related="category_id.account_depreciation_id",
        readonly=True,
    )
    account_expense_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        related="category_id.account_expense_id",
        readonly=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        related="category_id.journal_id",
        readonly=True,
    )

    @api.depends("original_value", "depreciation_line_ids.amount", "depreciation_line_ids.move_posted")
    def _compute_book_value(self):
        for asset in self:
            posted_lines = asset.depreciation_line_ids.filtered(lambda l: l.move_posted)
            asset.accumulated_depreciation = sum(posted_lines.mapped("amount"))
            asset.book_value = asset.original_value - asset.accumulated_depreciation

    @api.depends("date_start", "method_number", "method_period")
    def _compute_date_end(self):
        for asset in self:
            if asset.date_start and asset.method_number and asset.method_period:
                months = asset.method_number * int(asset.method_period)
                asset.date_end = asset.date_start + relativedelta(months=months)
            else:
                asset.date_end = False

    def action_confirm(self):
        """Confirm asset and generate depreciation schedule."""
        for asset in self:
            if not asset.depreciation_line_ids:
                asset._compute_depreciation_board()
            asset.state = "open"

    def action_close(self):
        """Close asset (fully depreciated or disposed)."""
        self.state = "close"

    def action_set_to_draft(self):
        """Reset to draft state."""
        self.state = "draft"

    def _compute_depreciation_board(self):
        """Generate depreciation schedule."""
        self.ensure_one()
        self.depreciation_line_ids.unlink()

        if self.method == "linear":
            self._compute_linear_depreciation()
        elif self.method == "degressive":
            self._compute_degressive_depreciation()

    def _compute_linear_depreciation(self):
        """Calculate straight-line depreciation."""
        depreciable_value = self.original_value - self.salvage_value
        depreciation_amount = depreciable_value / self.method_number

        current_date = self.date_start
        months = int(self.method_period)

        for i in range(self.method_number):
            self.env["account.asset.depreciation.line"].create({
                "asset_id": self.id,
                "sequence": i + 1,
                "depreciation_date": current_date + relativedelta(months=months * (i + 1)),
                "amount": depreciation_amount,
                "remaining_value": depreciable_value - (depreciation_amount * (i + 1)),
            })

    def _compute_degressive_depreciation(self):
        """Calculate declining balance depreciation."""
        remaining_value = self.original_value - self.salvage_value
        rate = 2.0 / self.method_number  # Double declining balance

        current_date = self.date_start
        months = int(self.method_period)

        for i in range(self.method_number):
            depreciation_amount = remaining_value * rate
            remaining_value -= depreciation_amount

            self.env["account.asset.depreciation.line"].create({
                "asset_id": self.id,
                "sequence": i + 1,
                "depreciation_date": current_date + relativedelta(months=months * (i + 1)),
                "amount": depreciation_amount,
                "remaining_value": max(remaining_value, self.salvage_value),
            })


class AccountAssetDepreciationLine(models.Model):
    """Depreciation schedule line."""

    _name = "account.asset.depreciation.line"
    _description = "Asset Depreciation Line"
    _order = "asset_id, sequence"

    asset_id = fields.Many2one(
        "account.asset",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer()
    depreciation_date = fields.Date(required=True)
    amount = fields.Monetary(
        currency_field="currency_id",
    )
    remaining_value = fields.Monetary(
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        related="asset_id.currency_id",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
    )
    move_posted = fields.Boolean(
        related="move_id.state",
        string="Posted",
        store=True,
    )

    def action_create_move(self):
        """Create depreciation journal entry."""
        for line in self:
            if line.move_id:
                raise UserError("Journal entry already exists for this line.")

            asset = line.asset_id
            move_vals = {
                "date": line.depreciation_date,
                "journal_id": asset.journal_id.id,
                "ref": f"Depreciation: {asset.name}",
                "line_ids": [
                    (0, 0, {
                        "name": f"Depreciation: {asset.name}",
                        "account_id": asset.account_expense_id.id,
                        "debit": line.amount,
                        "credit": 0,
                    }),
                    (0, 0, {
                        "name": f"Accumulated Depreciation: {asset.name}",
                        "account_id": asset.account_depreciation_id.id,
                        "debit": 0,
                        "credit": line.amount,
                    }),
                ],
            }
            move = self.env["account.move"].create(move_vals)
            line.move_id = move.id
