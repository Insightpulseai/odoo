# -*- coding: utf-8 -*-
from odoo import fields, models


class AssetCategory(models.Model):
    """Asset category for grouping and default policies."""

    _name = "ipai.asset.category"
    _description = "Asset Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()

    # Policies
    requires_approval = fields.Boolean(
        string="Requires Checkout Approval",
        default=False,
        help="If checked, checkouts of this category require manager approval",
    )
    max_checkout_days = fields.Integer(
        string="Max Checkout Duration (Days)",
        default=30,
        help="Maximum number of days an asset can be checked out",
    )
    allow_reservations = fields.Boolean(default=True)

    # Linked assets
    asset_ids = fields.One2many("ipai.asset", "category_id", string="Assets")
    asset_count = fields.Integer(compute="_compute_asset_count")

    def _compute_asset_count(self):
        for rec in self:
            rec.asset_count = len(rec.asset_ids)
