# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class AssetCheckout(models.Model):
    """Asset checkout record."""

    _name = "ipai.asset.checkout"
    _description = "Asset Checkout"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "checkout_date desc"

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )
    asset_id = fields.Many2one(
        "ipai.asset",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Checked Out To",
        required=True,
        tracking=True,
    )

    # Dates
    checkout_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    expected_return_date = fields.Date(tracking=True)
    actual_return_date = fields.Datetime(tracking=True)

    # Approval
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Approval"),
            ("active", "Active"),
            ("returned", "Returned"),
            ("overdue", "Overdue"),
        ],
        default="draft",
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", tracking=True)
    approval_date = fields.Datetime()

    # Notes
    checkout_notes = fields.Text()
    return_notes = fields.Text()
    condition_on_return = fields.Selection(
        [
            ("good", "Good"),
            ("damaged", "Damaged"),
            ("needs_repair", "Needs Repair"),
        ],
    )

    @api.depends("asset_id", "employee_id", "checkout_date")
    def _compute_name(self):
        for rec in self:
            if rec.asset_id and rec.employee_id:
                date_str = rec.checkout_date.strftime("%Y-%m-%d") if rec.checkout_date else ""
                rec.name = f"{rec.asset_id.name} - {rec.employee_id.name} ({date_str})"
            else:
                rec.name = "New Checkout"

    @api.constrains("asset_id", "state")
    def _check_asset_available(self):
        for rec in self:
            if rec.state in ("pending", "active"):
                other_active = self.search([
                    ("asset_id", "=", rec.asset_id.id),
                    ("state", "in", ("pending", "active")),
                    ("id", "!=", rec.id),
                ])
                if other_active:
                    raise ValidationError(
                        f"Asset {rec.asset_id.name} is already checked out or pending."
                    )

    def action_request_approval(self):
        """Submit for approval."""
        for rec in self:
            if rec.asset_id.category_id.requires_approval:
                rec.state = "pending"
            else:
                rec.action_approve()

    def action_approve(self):
        """Approve and activate checkout."""
        for rec in self:
            rec.write({
                "state": "active",
                "approved_by": self.env.user.id,
                "approval_date": fields.Datetime.now(),
            })
            rec.asset_id.write({
                "state": "checked_out",
                "custodian_id": rec.employee_id.id,
            })

    def action_check_in(self):
        """Return the asset."""
        for rec in self:
            rec.write({
                "state": "returned",
                "actual_return_date": fields.Datetime.now(),
            })
            rec.asset_id.write({
                "state": "available",
                "custodian_id": False,
            })
