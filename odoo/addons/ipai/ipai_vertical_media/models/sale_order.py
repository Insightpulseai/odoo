# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ces_campaign_id = fields.Char(
        string="CES Campaign ID",
        help="External CES campaign identifier, shared with Project.",
        index=True,
    )
    ces_budget_bucket = fields.Selection(
        [
            ("production", "Production"),
            ("media", "Media Placement"),
            ("fees", "Agency Fees"),
            ("talent", "Talent/Endorser"),
            ("research", "Research"),
            ("other", "Other"),
        ],
        string="CES Budget Bucket",
        help="Budget classification for CES analytics.",
    )
    ces_project_id = fields.Many2one(
        "project.project",
        string="CES Campaign Project",
        help="Link to the campaign project.",
        domain="[('ces_campaign_id', '!=', False)]",
    )
    ces_brand = fields.Char(
        string="Brand (CES)",
        related="ces_project_id.ces_brand",
        store=True,
        readonly=True,
    )
    ces_client = fields.Char(
        string="Client (CES)",
        related="ces_project_id.ces_client",
        store=True,
        readonly=True,
    )
    ces_is_rebillable = fields.Boolean(
        string="Rebillable",
        default=True,
        help="Whether this order is rebillable to client.",
    )
    ces_margin_percent = fields.Float(
        string="Target Margin %",
        help="Target margin percentage for this order.",
    )
    ces_po_number = fields.Char(
        string="Client PO Number",
        help="Client's purchase order number.",
    )
    ces_supplier_type = fields.Selection(
        [
            ("production_house", "Production House"),
            ("media_owner", "Media Owner"),
            ("talent", "Talent/Agency"),
            ("freelancer", "Freelancer"),
            ("tech_vendor", "Tech Vendor"),
            ("other", "Other"),
        ],
        string="Supplier Type",
        help="Classification of supplier for CES reporting.",
    )

    @api.onchange("ces_project_id")
    def _onchange_ces_project_id(self):
        """Auto-fill CES campaign ID from linked project."""
        if self.ces_project_id:
            self.ces_campaign_id = self.ces_project_id.ces_campaign_id


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ces_deliverable_type = fields.Selection(
        [
            ("tvc", "TVC Production"),
            ("avp", "AVP/Video"),
            ("print", "Print Material"),
            ("digital", "Digital Asset"),
            ("ooh", "OOH Material"),
            ("radio", "Radio Spot"),
            ("event", "Event/Activation"),
            ("talent", "Talent Fee"),
            ("media_buy", "Media Buy"),
            ("research", "Research"),
            ("other", "Other"),
        ],
        string="Deliverable Type",
        help="Type of deliverable for CES tracking.",
    )
    ces_cost_center = fields.Char(
        string="Cost Center",
        help="Internal cost center code.",
    )
