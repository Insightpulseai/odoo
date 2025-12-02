# -*- coding: utf-8 -*-
"""
IPAI Equipment Management Models.

This module provides Cheqroom-style equipment tracking functionality including:
- Equipment asset catalog with condition and status tracking
- Booking management with conflict detection and overdue monitoring
- Incident reporting and resolution tracking

Models:
    IpaiEquipmentAsset: Physical equipment items in the catalog
    IpaiEquipmentBooking: Equipment reservations and checkouts
    IpaiEquipmentIncident: Damage/issue reports for equipment
"""
from odoo import api, fields, models


class IpaiEquipmentAsset(models.Model):
    """
    Equipment Asset Model.

    Represents a physical piece of equipment that can be booked and tracked.
    Supports condition monitoring (new/good/used/damaged) and availability
    status (available/reserved/checked_out/maintenance).

    Attributes:
        _name: ipai.equipment.asset
        _description: IPAI Equipment Asset
    """

    _name = "ipai.equipment.asset"
    _description = "IPAI Equipment Asset"
    _order = "name"

    name = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Product")
    category_id = fields.Many2one("product.category", string="Category")
    serial_number = fields.Char()
    location_id = fields.Many2one("stock.location", string="Storage Location")
    condition = fields.Selection(
        [
            ("new", "New"),
            ("good", "Good"),
            ("used", "Used"),
            ("damaged", "Damaged"),
        ],
        default="good",
        required=True,
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("checked_out", "Checked Out"),
            ("maintenance", "In Maintenance"),
        ],
        default="available",
        required=True,
    )
    image_1920 = fields.Image("Image")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id
    )

    # Smart button fields
    booking_count = fields.Integer(
        string="Bookings",
        compute="_compute_booking_count",
        help="Number of bookings for this asset",
    )
    incident_count = fields.Integer(
        string="Incidents",
        compute="_compute_incident_count",
        help="Number of incidents reported for this asset",
    )

    @api.depends("name")
    def _compute_booking_count(self):
        """Count bookings for this asset"""
        for asset in self:
            asset.booking_count = self.env["ipai.equipment.booking"].search_count(
                [("asset_id", "=", asset.id)]
            )

    @api.depends("name")
    def _compute_incident_count(self):
        """Count incidents for this asset"""
        for asset in self:
            asset.incident_count = self.env["ipai.equipment.incident"].search_count(
                [("asset_id", "=", asset.id)]
            )

    def action_view_bookings(self):
        """Smart button action to view bookings"""
        return {
            "type": "ir.actions.act_window",
            "name": "Bookings",
            "res_model": "ipai.equipment.booking",
            "view_mode": "tree,form",
            "domain": [("asset_id", "=", self.id)],
            "context": {"default_asset_id": self.id},
        }

    def action_view_incidents(self):
        """Smart button action to view incidents"""
        return {
            "type": "ir.actions.act_window",
            "name": "Incidents",
            "res_model": "ipai.equipment.incident",
            "view_mode": "tree,form",
            "domain": [("asset_id", "=", self.id)],
            "context": {"default_asset_id": self.id},
        }


class IpaiEquipmentBooking(models.Model):
    """
    Equipment Booking Model.

    Manages equipment reservations and checkouts with automatic conflict detection.
    Tracks the full booking lifecycle: draft → reserved → checked_out → returned.

    Workflow:
        1. Create booking in draft state
        2. Reserve equipment (validates no conflicts)
        3. Check out to borrower
        4. Return equipment (releases asset)

    Attributes:
        _name: ipai.equipment.booking
        _description: IPAI Equipment Booking
    """

    _name = "ipai.equipment.booking"
    _description = "IPAI Equipment Booking"
    _order = "start_datetime desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "ipai.equipment.booking"
        ),
    )
    asset_id = fields.Many2one("ipai.equipment.asset", string="Asset", required=True)
    borrower_id = fields.Many2one("res.users", string="Borrower", required=True)
    project_id = fields.Many2one("project.project", string="Project / Job")
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("checked_out", "Checked Out"),
            ("returned", "Returned"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True,
        help="Booking is past end_datetime and still checked out",
    )

    @api.depends("end_datetime", "state")
    def _compute_is_overdue(self):
        """Check if booking is overdue (past end date and still checked out)"""
        now = fields.Datetime.now()
        for booking in self:
            booking.is_overdue = (
                booking.state == "checked_out"
                and booking.end_datetime
                and booking.end_datetime < now
            )

    @api.constrains("asset_id", "start_datetime", "end_datetime", "state")
    def _check_booking_conflict(self):
        """
        Validate no overlapping bookings exist for the same asset.

        Raises:
            ValueError: If the asset is already reserved or checked out
                during the requested time period.
        """
        for rec in self:
            if not rec.asset_id or not rec.start_datetime or not rec.end_datetime:
                continue
            domain = [
                ("id", "!=", rec.id),
                ("asset_id", "=", rec.asset_id.id),
                ("state", "in", ["reserved", "checked_out"]),
                ("start_datetime", "<", rec.end_datetime),
                ("end_datetime", ">", rec.start_datetime),
            ]
            if self.search_count(domain):
                raise ValueError(
                    "Booking conflict: asset already reserved/checked out in this period."
                )

    def action_reserve(self):
        """
        Confirm the booking and reserve the equipment.

        Sets booking state to 'reserved' and updates the linked asset
        status to 'reserved', preventing other bookings.
        """
        for rec in self:
            rec.state = "reserved"
            rec.asset_id.status = "reserved"

    def action_check_out(self):
        """
        Check out equipment to the borrower.

        Sets booking state to 'checked_out' and updates the linked asset
        status. Equipment is now physically with the borrower.
        """
        for rec in self:
            rec.state = "checked_out"
            rec.asset_id.status = "checked_out"

    def action_return(self):
        """
        Process equipment return from borrower.

        Sets booking state to 'returned' and releases the asset back to
        'available' status for future bookings.
        """
        for rec in self:
            rec.state = "returned"
            rec.asset_id.status = "available"

    def action_cancel(self):
        """
        Cancel the booking and release the equipment.

        Sets booking state to 'cancelled'. If the asset was reserved or
        checked out for this booking, releases it back to 'available'.
        """
        for rec in self:
            rec.state = "cancelled"
            if rec.asset_id.status in ("reserved", "checked_out"):
                rec.asset_id.status = "available"


class IpaiEquipmentIncident(models.Model):
    """
    Equipment Incident Model.

    Tracks damage, loss, or issues reported for equipment assets.
    Supports severity classification (low/medium/high) and resolution tracking.

    Can be linked to a specific booking to identify when/how damage occurred.

    Attributes:
        _name: ipai.equipment.incident
        _description: IPAI Equipment Incident
    """

    _name = "ipai.equipment.incident"
    _description = "IPAI Equipment Incident"
    _order = "create_date desc"

    name = fields.Char(required=True)
    booking_id = fields.Many2one("ipai.equipment.booking", string="Booking")
    asset_id = fields.Many2one("ipai.equipment.asset", string="Asset", required=True)
    reported_by = fields.Many2one("res.users", string="Reported By", required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low",
        required=True,
    )
    description = fields.Text()
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
        ],
        default="open",
        required=True,
    )
