# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssetReservation(models.Model):
    """Asset reservation for future checkout."""

    _name = "ipai.asset.reservation"
    _description = "Asset Reservation"
    _inherit = ["mail.thread"]
    _order = "start_date"

    name = fields.Char(compute="_compute_name", store=True)
    asset_id = fields.Many2one("ipai.asset", required=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Reserved For",
        required=True,
        tracking=True,
    )

    start_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("checked_out", "Checked Out"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        default="draft",
        tracking=True,
    )
    notes = fields.Text()

    @api.depends("asset_id", "employee_id", "start_date")
    def _compute_name(self):
        for rec in self:
            if rec.asset_id and rec.employee_id:
                rec.name = f"{rec.asset_id.name} - {rec.employee_id.name} ({rec.start_date})"
            else:
                rec.name = "New Reservation"

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError("End date must be after start date.")

    @api.constrains("asset_id", "start_date", "end_date", "state")
    def _check_overlap(self):
        for rec in self:
            if rec.state not in ("draft", "cancelled", "expired"):
                overlapping = self.search([
                    ("asset_id", "=", rec.asset_id.id),
                    ("id", "!=", rec.id),
                    ("state", "not in", ("cancelled", "expired")),
                    ("start_date", "<=", rec.end_date),
                    ("end_date", ">=", rec.start_date),
                ])
                if overlapping:
                    raise ValidationError(
                        f"Reservation overlaps with existing reservation: {overlapping[0].name}"
                    )

    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"
            rec.asset_id.state = "reserved"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
            if not rec.asset_id.reservation_ids.filtered(
                lambda r: r.state == "confirmed" and r.id != rec.id
            ):
                rec.asset_id.state = "available"

    def action_convert_to_checkout(self):
        """Convert reservation to active checkout."""
        for rec in self:
            checkout = self.env["ipai.asset.checkout"].create({
                "asset_id": rec.asset_id.id,
                "employee_id": rec.employee_id.id,
                "expected_return_date": rec.end_date,
                "checkout_notes": f"From reservation: {rec.name}",
            })
            checkout.action_approve()
            rec.state = "checked_out"
        return checkout
