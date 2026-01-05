# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Asset(models.Model):
    """Individual asset that can be checked out."""

    _name = "ipai.asset"
    _description = "Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        string="Asset Code",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.asset"),
    )
    barcode = fields.Char(tracking=True, help="Barcode or QR code for scanning")

    category_id = fields.Many2one(
        "ipai.asset.category",
        required=True,
        tracking=True,
    )
    description = fields.Text()
    image = fields.Image(max_width=512, max_height=512)

    # Status
    state = fields.Selection(
        [
            ("available", "Available"),
            ("checked_out", "Checked Out"),
            ("reserved", "Reserved"),
            ("maintenance", "In Maintenance"),
            ("retired", "Retired"),
        ],
        default="available",
        tracking=True,
    )

    # Financial
    purchase_date = fields.Date()
    purchase_value = fields.Monetary(currency_field="currency_id")
    current_value = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_current_value",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Location
    location_id = fields.Many2one("stock.location", string="Current Location")
    custodian_id = fields.Many2one(
        "hr.employee",
        string="Current Custodian",
        tracking=True,
    )

    # Relationships
    checkout_ids = fields.One2many("ipai.asset.checkout", "asset_id")
    reservation_ids = fields.One2many("ipai.asset.reservation", "asset_id")

    # Computed
    active_checkout_id = fields.Many2one(
        "ipai.asset.checkout",
        compute="_compute_active_checkout",
        string="Active Checkout",
    )

    @api.depends("checkout_ids", "checkout_ids.state")
    def _compute_active_checkout(self):
        for rec in self:
            active = rec.checkout_ids.filtered(lambda c: c.state == "active")
            rec.active_checkout_id = active[:1] if active else False

    @api.depends("purchase_value", "purchase_date")
    def _compute_current_value(self):
        # Simple straight-line depreciation placeholder
        for rec in self:
            rec.current_value = rec.purchase_value

    def action_check_out(self):
        """Open checkout wizard."""
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.asset.checkout",
            "view_mode": "form",
            "target": "new",
            "context": {"default_asset_id": self.id},
        }

    def action_check_in(self):
        """Check in the active checkout."""
        if self.active_checkout_id:
            self.active_checkout_id.action_check_in()
