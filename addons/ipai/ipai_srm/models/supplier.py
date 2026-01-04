# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SrmSupplier(models.Model):
    """Extended supplier profile with SRM attributes."""

    _name = "srm.supplier"
    _description = "SRM Supplier Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        string="Supplier Code",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("srm.supplier"),
    )
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]",
    )

    # Classification
    tier = fields.Selection(
        [
            ("strategic", "Strategic"),
            ("preferred", "Preferred"),
            ("approved", "Approved"),
            ("conditional", "Conditional"),
            ("inactive", "Inactive"),
        ],
        default="approved",
        tracking=True,
    )
    category_ids = fields.Many2many(
        "product.category",
        string="Product Categories",
        help="Categories this supplier provides",
    )

    # Status
    state = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("qualification", "In Qualification"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("blocked", "Blocked"),
            ("archived", "Archived"),
        ],
        default="prospect",
        tracking=True,
    )

    # Scores
    overall_score = fields.Float(
        compute="_compute_overall_score",
        store=True,
        tracking=True,
    )
    scorecard_ids = fields.One2many("srm.scorecard", "supplier_id")
    latest_scorecard_id = fields.Many2one(
        "srm.scorecard",
        compute="_compute_latest_scorecard",
    )

    # Risk
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="medium",
        tracking=True,
    )
    risk_notes = fields.Text()

    # Qualification
    qualification_ids = fields.One2many("srm.qualification", "supplier_id")
    is_qualified = fields.Boolean(compute="_compute_is_qualified", store=True)
    qualification_expiry = fields.Date()

    # Compliance
    compliance_docs_complete = fields.Boolean(default=False)
    last_audit_date = fields.Date()
    next_audit_date = fields.Date()

    # Contacts
    primary_contact_id = fields.Many2one("res.partner")
    sales_contact_id = fields.Many2one("res.partner")

    # Spending
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    ytd_spend = fields.Monetary(
        string="YTD Spend",
        currency_field="currency_id",
        compute="_compute_ytd_spend",
    )
    total_po_count = fields.Integer(compute="_compute_po_stats")
    open_po_count = fields.Integer(compute="_compute_po_stats")

    @api.depends("scorecard_ids", "scorecard_ids.overall_score")
    def _compute_overall_score(self):
        for rec in self:
            if rec.scorecard_ids:
                latest = rec.scorecard_ids.sorted("as_of", reverse=True)[:1]
                rec.overall_score = latest.overall_score if latest else 0
            else:
                rec.overall_score = 0

    @api.depends("scorecard_ids")
    def _compute_latest_scorecard(self):
        for rec in self:
            rec.latest_scorecard_id = rec.scorecard_ids.sorted("as_of", reverse=True)[
                :1
            ]

    @api.depends("qualification_ids", "qualification_ids.state")
    def _compute_is_qualified(self):
        for rec in self:
            approved = rec.qualification_ids.filtered(lambda q: q.state == "approved")
            rec.is_qualified = bool(approved)

    def _compute_ytd_spend(self):
        # Placeholder - would compute from purchase.order
        for rec in self:
            rec.ytd_spend = 0

    def _compute_po_stats(self):
        # Placeholder - would compute from purchase.order
        for rec in self:
            rec.total_po_count = 0
            rec.open_po_count = 0

    def action_start_qualification(self):
        """Start supplier qualification process."""
        return {
            "type": "ir.actions.act_window",
            "res_model": "srm.qualification",
            "view_mode": "form",
            "target": "new",
            "context": {"default_supplier_id": self.id},
        }

    def action_create_scorecard(self):
        """Create a new scorecard evaluation."""
        return {
            "type": "ir.actions.act_window",
            "res_model": "srm.scorecard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_supplier_id": self.id},
        }

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_block(self):
        for rec in self:
            rec.state = "blocked"
