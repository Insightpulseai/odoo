# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SrmScorecard(models.Model):
    """Supplier scorecard evaluation."""

    _name = "srm.scorecard"
    _description = "Supplier Scorecard"
    _inherit = ["mail.thread"]
    _order = "as_of desc"

    name = fields.Char(compute="_compute_name", store=True)
    supplier_id = fields.Many2one(
        "srm.supplier",
        required=True,
        tracking=True,
    )
    as_of = fields.Date(
        string="Evaluation Date",
        default=fields.Date.today,
        required=True,
    )
    period = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        default="quarterly",
    )

    # KPI Lines
    line_ids = fields.One2many("srm.scorecard.line", "scorecard_id")

    # Overall Score
    overall_score = fields.Float(
        compute="_compute_overall_score",
        store=True,
    )
    grade = fields.Selection(
        [
            ("A", "A - Excellent"),
            ("B", "B - Good"),
            ("C", "C - Acceptable"),
            ("D", "D - Needs Improvement"),
            ("F", "F - Unacceptable"),
        ],
        compute="_compute_grade",
        store=True,
    )

    # Evaluation
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
        ],
        default="draft",
        tracking=True,
    )
    evaluator_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    comments = fields.Text()
    action_items = fields.Text()

    @api.depends("supplier_id", "as_of")
    def _compute_name(self):
        for rec in self:
            if rec.supplier_id and rec.as_of:
                rec.name = f"{rec.supplier_id.name} - {rec.as_of}"
            else:
                rec.name = "New Scorecard"

    @api.depends("line_ids", "line_ids.score", "line_ids.weight")
    def _compute_overall_score(self):
        for rec in self:
            if rec.line_ids:
                total_weight = sum(rec.line_ids.mapped("weight"))
                if total_weight:
                    weighted_sum = sum(
                        line.score * line.weight for line in rec.line_ids
                    )
                    rec.overall_score = weighted_sum / total_weight
                else:
                    rec.overall_score = 0
            else:
                rec.overall_score = 0

    @api.depends("overall_score")
    def _compute_grade(self):
        for rec in self:
            score = rec.overall_score
            if score >= 90:
                rec.grade = "A"
            elif score >= 80:
                rec.grade = "B"
            elif score >= 70:
                rec.grade = "C"
            elif score >= 60:
                rec.grade = "D"
            else:
                rec.grade = "F"

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"

    @api.model
    def create(self, vals):
        """Auto-populate KPI lines from categories."""
        record = super().create(vals)
        if not record.line_ids:
            categories = self.env["srm.kpi.category"].search([])
            for cat in categories:
                self.env["srm.scorecard.line"].create({
                    "scorecard_id": record.id,
                    "kpi_category_id": cat.id,
                    "weight": cat.weight,
                })
        return record


class SrmScorecardLine(models.Model):
    """Individual KPI score in a scorecard."""

    _name = "srm.scorecard.line"
    _description = "Scorecard Line"
    _order = "sequence"

    scorecard_id = fields.Many2one("srm.scorecard", required=True, ondelete="cascade")
    kpi_category_id = fields.Many2one("srm.kpi.category", required=True)
    sequence = fields.Integer(related="kpi_category_id.sequence", store=True)

    weight = fields.Float(string="Weight (%)")
    score = fields.Float(string="Score (0-100)", default=70)
    weighted_score = fields.Float(compute="_compute_weighted_score", store=True)

    notes = fields.Text()
    evidence = fields.Text()

    @api.depends("score", "weight")
    def _compute_weighted_score(self):
        for rec in self:
            rec.weighted_score = rec.score * (rec.weight / 100) if rec.weight else 0
