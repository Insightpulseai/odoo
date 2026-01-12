# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrObjective(models.Model):
    """OKR Objective for Finance Governance.

    Strategic objectives (e.g., "Achieve fully compliant, predictable
    month-end close and tax filing") with 3-5 measurable Key Results.
    """

    _name = "okr.objective"
    _description = "OKR Objective"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc, name"

    name = fields.Char(
        string="Objective",
        required=True,
        tracking=True,
        help="Short label for the strategic objective",
    )
    description = fields.Text(
        string="Description",
        tracking=True,
        help="Qualitative objective statement",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help="Person accountable for this objective",
    )
    period_start = fields.Date(
        string="Period Start",
        required=True,
        tracking=True,
        help="Start of the OKR period (e.g., Q1 start)",
    )
    period_end = fields.Date(
        string="Period End",
        required=True,
        tracking=True,
        help="End of the OKR period (e.g., Q1 end)",
    )
    portfolio_id = fields.Many2one(
        "project.project",
        string="Portfolio/Program",
        tracking=True,
        help="Optional link to a PPM portfolio or program project",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    key_result_ids = fields.One2many(
        "okr.key.result",
        "objective_id",
        string="Key Results",
    )
    overall_score = fields.Float(
        string="Overall Score",
        compute="_compute_overall_score",
        store=True,
        digits=(3, 2),
        help="Average score (0.0-1.0) of all Key Results",
    )
    confidence = fields.Integer(
        string="Overall Confidence",
        default=50,
        tracking=True,
        help="Confidence level (0-100%) in achieving this objective",
    )

    # PPM/PMBOK alignment notes (text fields for governance)
    scope_notes = fields.Text(
        string="Scope Notes",
        help="PMBOK scope considerations",
    )
    schedule_notes = fields.Text(
        string="Schedule Notes",
        help="PMBOK schedule considerations",
    )
    cost_notes = fields.Text(
        string="Cost Notes",
        help="PMBOK cost considerations",
    )
    quality_notes = fields.Text(
        string="Quality Notes",
        help="PMBOK quality considerations",
    )
    stakeholder_notes = fields.Text(
        string="Stakeholder Notes",
        help="Key stakeholders and communication approach",
    )
    communication_cadence = fields.Char(
        string="Communication Cadence",
        default="Weekly Dashboard",
        help="How often this objective is reviewed (e.g., weekly dashboard)",
    )

    @api.depends("key_result_ids.status_score")
    def _compute_overall_score(self):
        """Compute average score from all Key Results."""
        for obj in self:
            scores = obj.mapped("key_result_ids.status_score")
            obj.overall_score = sum(scores) / len(scores) if scores else 0.0

    def action_activate(self):
        """Activate the objective."""
        self.write({"state": "active"})

    def action_close(self):
        """Close the objective."""
        self.write({"state": "closed"})

    def action_cancel(self):
        """Cancel the objective."""
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        """Reset to draft state."""
        self.write({"state": "draft"})
