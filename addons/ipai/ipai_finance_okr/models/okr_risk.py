# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrRisk(models.Model):
    """Risk Register linked to OKR Key Results.

    When KR confidence drops below 40%, a risk entry should be created
    to track mitigation actions.
    """

    _name = "okr.risk"
    _description = "OKR Risk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    PRIORITY_SELECTION = [
        ("0", "Low"),
        ("1", "Normal"),
        ("2", "High"),
        ("3", "Critical"),
    ]

    key_result_id = fields.Many2one(
        "okr.key.result",
        string="Key Result",
        ondelete="set null",
        tracking=True,
        help="The Key Result this risk affects (optional for standalone risks)",
    )
    name = fields.Char(
        string="Risk",
        required=True,
        tracking=True,
    )
    description = fields.Text(
        string="Description",
        tracking=True,
    )
    probability = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        string="Probability",
        default="medium",
        required=True,
        tracking=True,
    )
    impact = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Impact",
        default="medium",
        required=True,
        tracking=True,
    )
    response_strategy = fields.Selection(
        [
            ("accept", "Accept"),
            ("mitigate", "Mitigate"),
            ("avoid", "Avoid"),
            ("transfer", "Transfer"),
        ],
        string="Response Strategy",
        default="mitigate",
        required=True,
        tracking=True,
        help=(
            "Accept: No action needed. "
            "Mitigate: Reduce probability or impact. "
            "Avoid: Change plans to eliminate risk. "
            "Transfer: Shift risk to third party."
        ),
    )
    mitigation_plan = fields.Text(
        string="Mitigation Plan",
        tracking=True,
        help="Specific actions to reduce or eliminate this risk",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Risk Owner",
        tracking=True,
        default=lambda self: self.env.user,
    )
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("mitigated", "Mitigated"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
        required=True,
        tracking=True,
    )
    escalated = fields.Boolean(
        string="Escalated",
        default=False,
        tracking=True,
        help="Mark if this risk has been escalated to leadership",
    )
    priority = fields.Selection(
        PRIORITY_SELECTION,
        string="Priority",
        compute="_compute_priority",
        store=True,
    )
    date_identified = fields.Date(
        string="Date Identified",
        default=fields.Date.context_today,
    )
    date_target_resolution = fields.Date(
        string="Target Resolution Date",
    )
    date_resolved = fields.Date(
        string="Date Resolved",
    )

    # Related fields
    objective_id = fields.Many2one(
        related="key_result_id.objective_id",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.depends("probability", "impact")
    def _compute_priority(self):
        """Compute priority based on probability x impact matrix."""
        matrix = {
            ("low", "low"): "0",
            ("low", "medium"): "0",
            ("low", "high"): "1",
            ("low", "critical"): "2",
            ("medium", "low"): "0",
            ("medium", "medium"): "1",
            ("medium", "high"): "2",
            ("medium", "critical"): "3",
            ("high", "low"): "1",
            ("high", "medium"): "2",
            ("high", "high"): "3",
            ("high", "critical"): "3",
        }
        for risk in self:
            risk.priority = matrix.get(
                (risk.probability, risk.impact), "1"
            )

    def action_mitigate(self):
        """Mark risk as being mitigated."""
        self.write({"status": "in_progress"})

    def action_close(self):
        """Close the risk."""
        self.write({
            "status": "closed",
            "date_resolved": fields.Date.context_today(self),
        })

    def action_escalate(self):
        """Escalate the risk."""
        self.write({"escalated": True})
