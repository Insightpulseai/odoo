# -*- coding: utf-8 -*-
import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class QuoteCalculatorConfig(models.Model):
    """Quote calculator configuration for pricing rules."""
    _name = "ipai.quote.calculator.config"
    _description = "IPAI Quote Calculator Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Configuration Name", required=True, tracking=True)
    code = fields.Char(string="Config Code", tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)

    pricing_rules = fields.Text(
        string="Pricing Rules (JSON)",
        help="JSON structure for pricing rules and conditions",
        default="{}",
    )

    user_count_bands = fields.Text(
        string="User Count Bands (JSON)",
        help="JSON structure for user count pricing bands",
        default='[{"min": 1, "max": 10, "multiplier": 1.0}, {"min": 11, "max": 50, "multiplier": 1.5}]',
    )

    app_bundle_rules = fields.Text(
        string="App Bundle Rules (JSON)",
        help="JSON structure for app bundle pricing",
        default="{}",
    )

    base_hourly_rate = fields.Float(
        string="Base Hourly Rate",
        default=150.0,
        tracking=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    description = fields.Text(string="Description")

    def get_pricing_rules_dict(self):
        """Return pricing rules as Python dict."""
        self.ensure_one()
        try:
            return json.loads(self.pricing_rules or "{}")
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in pricing_rules for config %s", self.name)
            return {}

    def get_user_count_bands_list(self):
        """Return user count bands as Python list."""
        self.ensure_one()
        try:
            return json.loads(self.user_count_bands or "[]")
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in user_count_bands for config %s", self.name)
            return []


class QuoteCalculatorRun(models.Model):
    """Quote calculator execution/run record."""
    _name = "ipai.quote.calculator.run"
    _description = "IPAI Quote Calculator Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Run Reference",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("calculated", "Calculated"),
        ("quoted", "Quote Created"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="draft", tracking=True)

    config_id = fields.Many2one(
        "ipai.quote.calculator.config",
        string="Calculator Config",
        required=True,
        tracking=True,
    )

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead/Opportunity",
        tracking=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        tracking=True,
    )

    # Input parameters
    inputs_json = fields.Text(
        string="Calculator Inputs (JSON)",
        help="JSON structure of all calculator inputs",
        default="{}",
    )

    user_count = fields.Integer(
        string="User Count",
        help="Number of users for implementation",
    )

    app_count = fields.Integer(
        string="App Count",
        help="Number of Odoo apps to implement",
    )

    complexity = fields.Selection([
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("very_high", "Very High"),
    ], string="Complexity", default="medium")

    # Output / results
    recommended_pack_id = fields.Many2one(
        "ipai.service.pack",
        string="Recommended Pack",
        tracking=True,
    )

    computed_lines = fields.Text(
        string="Computed Lines (JSON)",
        help="JSON structure of computed quote lines",
        default="[]",
    )

    estimated_hours = fields.Float(
        string="Estimated Hours",
        compute="_compute_totals",
        store=True,
    )

    estimated_amount = fields.Monetary(
        string="Estimated Amount",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="config_id.currency_id",
        store=True,
    )

    # Link to generated quote
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Generated Quote",
        readonly=True,
        copy=False,
    )

    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "ipai.quote.calculator.run"
                ) or _("New")
        return super().create(vals_list)

    @api.depends("computed_lines", "config_id.base_hourly_rate")
    def _compute_totals(self):
        for run in self:
            total_hours = 0.0
            try:
                lines = json.loads(run.computed_lines or "[]")
                for line in lines:
                    total_hours += line.get("hours", 0)
            except json.JSONDecodeError:
                pass
            run.estimated_hours = total_hours
            run.estimated_amount = total_hours * (run.config_id.base_hourly_rate or 0)

    def action_calculate(self):
        """Run the quote calculation based on inputs."""
        self.ensure_one()
        if not self.config_id:
            raise UserError(_("Please select a calculator configuration."))

        # Get complexity multiplier
        complexity_map = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "very_high": 1.6,
        }
        complexity_mult = complexity_map.get(self.complexity, 1.0)

        # Get user count multiplier from bands
        user_mult = 1.0
        bands = self.config_id.get_user_count_bands_list()
        for band in bands:
            if band.get("min", 0) <= self.user_count <= band.get("max", 9999):
                user_mult = band.get("multiplier", 1.0)
                break

        # Base hours calculation
        base_hours = (self.app_count or 1) * 40  # 40 hours per app baseline

        # Apply multipliers
        total_hours = base_hours * complexity_mult * user_mult

        # Build computed lines
        lines = [
            {
                "description": "Requirements & Analysis",
                "hours": total_hours * 0.15,
                "phase": "discovery",
            },
            {
                "description": "Configuration & Setup",
                "hours": total_hours * 0.35,
                "phase": "implementation",
            },
            {
                "description": "Data Migration",
                "hours": total_hours * 0.20,
                "phase": "implementation",
            },
            {
                "description": "Testing & UAT",
                "hours": total_hours * 0.15,
                "phase": "testing",
            },
            {
                "description": "Training & Go-Live Support",
                "hours": total_hours * 0.15,
                "phase": "deployment",
            },
        ]

        self.write({
            "computed_lines": json.dumps(lines),
            "state": "calculated",
        })

        # Find recommended pack
        packs = self.env["ipai.service.pack"].search([
            ("active", "=", True),
            ("default_hours", ">=", total_hours * 0.8),
            ("default_hours", "<=", total_hours * 1.2),
        ], limit=1, order="default_hours asc")
        if packs:
            self.recommended_pack_id = packs[0].id

        return True

    def action_create_quote(self):
        """Create a sale order from the calculator run."""
        self.ensure_one()
        if self.state != "calculated":
            raise UserError(_("Please run the calculation first."))

        if not self.partner_id and not self.lead_id:
            raise UserError(_("Please set a customer or lead."))

        partner = self.partner_id or self.lead_id.partner_id
        if not partner:
            raise UserError(_("No customer found. Please set a customer."))

        # Create sale order
        so_vals = {
            "partner_id": partner.id,
            "opportunity_id": self.lead_id.id if self.lead_id else False,
            "origin": self.name,
        }

        # Find or create implementation service product
        product = self.env["product.product"].search([
            ("default_code", "=", "IMPL-SERVICE"),
        ], limit=1)
        if not product:
            product = self.env["product.product"].create({
                "name": "Implementation Services",
                "default_code": "IMPL-SERVICE",
                "type": "service",
                "list_price": self.config_id.base_hourly_rate or 150.0,
            })

        # Create order lines from computed lines
        order_lines = []
        try:
            lines = json.loads(self.computed_lines or "[]")
            for line in lines:
                order_lines.append((0, 0, {
                    "product_id": product.id,
                    "name": line.get("description", "Implementation Service"),
                    "product_uom_qty": line.get("hours", 0),
                    "price_unit": self.config_id.base_hourly_rate or 150.0,
                }))
        except json.JSONDecodeError:
            pass

        if order_lines:
            so_vals["order_line"] = order_lines

        sale_order = self.env["sale.order"].create(so_vals)
        self.write({
            "sale_order_id": sale_order.id,
            "state": "quoted",
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_cancel(self):
        """Cancel the calculator run."""
        self.write({"state": "cancelled"})

    def action_reset_draft(self):
        """Reset to draft state."""
        self.write({"state": "draft"})
