# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrKrMilestone(models.Model):
    """Milestones linked to Key Results.

    Track important checkpoints that indicate progress toward KRs.
    E.g., "Month-End Closed - Day-3", "All Taxes Filed This Period".
    """

    _name = "okr.kr.milestone"
    _description = "KR Milestone"
    _inherit = ["mail.thread"]
    _order = "key_result_id, date_planned, id"

    key_result_id = fields.Many2one(
        "okr.key.result",
        string="Key Result",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Milestone",
        required=True,
        tracking=True,
        help="E.g., 'Month-End Closed - Day-3'",
    )
    description = fields.Text(
        string="Description",
    )
    date_planned = fields.Date(
        string="Planned Date",
        tracking=True,
    )
    date_reached = fields.Date(
        string="Date Reached",
        tracking=True,
    )
    status = fields.Selection(
        [
            ("not_reached", "Not Reached"),
            ("reached", "Reached"),
            ("late", "Reached Late"),
        ],
        string="Status",
        default="not_reached",
        required=True,
        tracking=True,
        compute="_compute_status",
        store=True,
        readonly=False,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Optional link to a project",
    )

    # Related fields
    objective_id = fields.Many2one(
        related="key_result_id.objective_id",
        store=True,
    )
    company_id = fields.Many2one(
        related="key_result_id.company_id",
        store=True,
    )

    @api.depends("date_planned", "date_reached")
    def _compute_status(self):
        """Auto-compute status based on dates."""
        for milestone in self:
            if not milestone.date_reached:
                milestone.status = "not_reached"
            elif milestone.date_planned and milestone.date_reached > milestone.date_planned:
                milestone.status = "late"
            else:
                milestone.status = "reached"

    def action_mark_reached(self):
        """Mark milestone as reached today."""
        self.write({
            "date_reached": fields.Date.context_today(self),
        })

    def action_reset(self):
        """Reset milestone to not reached."""
        self.write({
            "date_reached": False,
            "status": "not_reached",
        })
