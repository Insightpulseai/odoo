# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectBudget(models.Model):
    _name = "ipai.project.budget"
    _description = "Project Budget"
    _order = "project_id, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Budget Name", compute="_compute_name", store=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id", store=True, readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="project_id.currency_id", store=True, readonly=True
    )
    budget_amount = fields.Monetary(
        string="Total Budget", currency_field="currency_id", tracking=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("closed", "Closed"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )
    line_ids = fields.One2many(
        "ipai.project.budget.line", "budget_id", string="Budget Lines"
    )
    planned_total = fields.Monetary(
        compute="_compute_totals",
        string="Planned Total",
        currency_field="currency_id",
        store=True,
    )
    actual_total = fields.Monetary(
        compute="_compute_totals",
        string="Actual Total",
        currency_field="currency_id",
        store=True,
    )
    variance = fields.Monetary(
        compute="_compute_totals",
        string="Variance",
        currency_field="currency_id",
        store=True,
        help="Positive = under budget, Negative = over budget",
    )
    variance_percent = fields.Float(
        compute="_compute_totals", string="Variance %", store=True
    )
    active = fields.Boolean(string="Active", default=True)
    notes = fields.Text(string="Notes")

    @api.depends("project_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = (
                f"Budget: {rec.project_id.name}" if rec.project_id else "New Budget"
            )

    @api.depends("budget_amount", "line_ids.planned_amount", "line_ids.actual_amount")
    def _compute_totals(self):
        for rec in self:
            rec.planned_total = sum(rec.line_ids.mapped("planned_amount"))
            rec.actual_total = sum(rec.line_ids.mapped("actual_amount"))
            rec.variance = rec.planned_total - rec.actual_total
            if rec.planned_total:
                rec.variance_percent = (rec.variance / rec.planned_total) * 100
            else:
                rec.variance_percent = 0.0

    def action_approve(self):
        """Approve the budget."""
        self.write({"state": "approved"})

    def action_close(self):
        """Close the budget."""
        self.write({"state": "closed"})

    def action_reset_to_draft(self):
        """Reset to draft state."""
        self.write({"state": "draft"})


class ProjectBudgetLine(models.Model):
    _name = "ipai.project.budget.line"
    _description = "Project Budget Line"
    _order = "sequence, id"

    budget_id = fields.Many2one(
        "ipai.project.budget",
        string="Budget",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(string="Description", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    currency_id = fields.Many2one(
        "res.currency", related="budget_id.currency_id", store=True, readonly=True
    )
    planned_amount = fields.Monetary(string="Planned", currency_field="currency_id")
    actual_amount = fields.Monetary(string="Actual", currency_field="currency_id")
    variance = fields.Monetary(
        compute="_compute_variance",
        string="Variance",
        currency_field="currency_id",
        store=True,
    )
    category = fields.Selection(
        [
            ("labor", "Labor"),
            ("materials", "Materials"),
            ("equipment", "Equipment"),
            ("travel", "Travel"),
            ("services", "Services"),
            ("other", "Other"),
        ],
        string="Category",
        default="other",
    )
    notes = fields.Text(string="Notes")

    @api.depends("planned_amount", "actual_amount")
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.planned_amount - rec.actual_amount
