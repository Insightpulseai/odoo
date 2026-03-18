# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError

from odoo import _, api, fields, models


class ServicePack(models.Model):
    """Service packaging for Odoo Partner implementations."""

    _name = "ipai.service.pack"
    _description = "IPAI Service Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Pack Name", required=True, tracking=True)
    code = fields.Char(string="Pack Code", tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)

    tier = fields.Selection(
        [
            ("starter", "Starter"),
            ("professional", "Professional"),
            ("enterprise", "Enterprise"),
            ("custom", "Custom"),
        ],
        string="Tier",
        required=True,
        default="professional",
        tracking=True,
    )

    default_hours = fields.Float(
        string="Default Hours",
        help="Estimated hours for this service pack",
        tracking=True,
    )

    ratio_impl_to_pm = fields.Float(
        string="Implementation to PM Ratio",
        default=4.0,
        help="Ratio of implementation hours to PM hours (e.g., 4:1)",
    )

    included_deliverables = fields.Text(
        string="Included Deliverables (JSON)",
        help="JSON structure defining included deliverables",
    )

    default_team_template_id = fields.Many2one(
        "ipai.implementation.template",
        string="Default Implementation Template",
    )

    description = fields.Html(string="Description")
    notes = fields.Text(string="Internal Notes")

    line_ids = fields.One2many(
        "ipai.service.pack.line",
        "service_pack_id",
        string="Pack Lines",
    )

    # Computed fields
    total_lines = fields.Integer(
        string="Total Lines",
        compute="_compute_totals",
        store=True,
    )
    total_quantity = fields.Float(
        string="Total Quantity",
        compute="_compute_totals",
        store=True,
    )

    @api.depends("line_ids", "line_ids.qty")
    def _compute_totals(self):
        for pack in self:
            pack.total_lines = len(pack.line_ids)
            pack.total_quantity = sum(pack.line_ids.mapped("qty"))

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Pack code must be unique!"),
    ]


class ServicePackLine(models.Model):
    """Service pack line items."""

    _name = "ipai.service.pack.line"
    _description = "IPAI Service Pack Line"
    _order = "sequence, id"

    service_pack_id = fields.Many2one(
        "ipai.service.pack",
        string="Service Pack",
        required=True,
        ondelete="cascade",
    )

    sequence = fields.Integer(string="Sequence", default=10)

    product_id = fields.Many2one(
        "product.product",
        string="Service/Product",
        required=True,
        domain="[('type', '=', 'service')]",
    )

    name = fields.Char(string="Description")
    qty = fields.Float(string="Quantity", default=1.0, required=True)

    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        readonly=True,
    )

    is_optional = fields.Boolean(
        string="Optional",
        help="Mark as optional add-on for the service pack",
    )

    role_mix = fields.Text(
        string="Role Mix (JSON)",
        help="JSON structure for team composition (e.g., consultant, PM, developer hours)",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
