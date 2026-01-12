# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrKeyResult(models.Model):
    """OKR Key Result - quantified measurable outcome for an Objective.

    Each Objective should have 3-5 Key Results. These are SMART metrics
    that define success criteria for the objective.

    Example KRs for Finance Month-End:
    - KR1: >=95% of close tasks finished by Day-3
    - KR2: 100% of taxes filed on time
    - KR3: Accrual variance < PHP 50k
    """

    _name = "okr.key.result"
    _description = "OKR Key Result"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "objective_id, sequence, id"

    objective_id = fields.Many2one(
        "okr.objective",
        string="Objective",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order of Key Results within an Objective",
    )
    name = fields.Char(
        string="Key Result",
        required=True,
        tracking=True,
        help="Short label for the key result (e.g., KR1 - Close by Day-3)",
    )
    metric_description = fields.Text(
        string="Metric Description",
        tracking=True,
        help="SMART metric definition (Specific, Measurable, Achievable, Relevant, Time-bound)",
    )
    baseline_value = fields.Float(
        string="Baseline",
        digits=(12, 2),
        tracking=True,
        help="Starting value at the beginning of the period",
    )
    target_value = fields.Float(
        string="Target",
        digits=(12, 2),
        tracking=True,
        help="Target value to achieve by the deadline",
    )
    current_value = fields.Float(
        string="Current Value",
        digits=(12, 2),
        tracking=True,
        help="Current measured value",
    )
    unit = fields.Char(
        string="Unit",
        default="%",
        tracking=True,
        help="Unit of measurement (%, count, PHP, etc.)",
    )
    deadline = fields.Date(
        string="Deadline",
        tracking=True,
        help="Target date to achieve this Key Result",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help="Person accountable for this Key Result",
    )
    status_score = fields.Float(
        string="Score (0-1.0)",
        default=0.0,
        digits=(3, 2),
        tracking=True,
        help="Achievement score: 0.0 = not started, 0.7 = good, 1.0 = fully achieved",
    )
    confidence = fields.Integer(
        string="Confidence (0-100)",
        default=50,
        tracking=True,
        help="Confidence level in achieving this KR. <40% triggers risk flag.",
    )
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Level",
        default="medium",
        tracking=True,
        compute="_compute_risk_level",
        store=True,
        help="Computed from confidence level",
    )
    direction = fields.Selection(
        [
            ("increase", "Increase"),
            ("decrease", "Decrease"),
            ("maintain", "Maintain"),
        ],
        string="Direction",
        default="increase",
        tracking=True,
        help="Whether the metric should increase, decrease, or be maintained",
    )

    # Related records
    score_snapshot_ids = fields.One2many(
        "okr.kr.score.snapshot",
        "key_result_id",
        string="Score History",
    )
    risk_ids = fields.One2many(
        "okr.risk",
        "key_result_id",
        string="Risks",
    )
    task_link_ids = fields.One2many(
        "okr.kr.task.link",
        "key_result_id",
        string="Linked Tasks",
    )
    milestone_ids = fields.One2many(
        "okr.kr.milestone",
        "key_result_id",
        string="Milestones",
    )

    # Computed fields
    company_id = fields.Many2one(
        related="objective_id.company_id",
        store=True,
    )
    progress_pct = fields.Float(
        string="Progress %",
        compute="_compute_progress_pct",
        help="Progress percentage toward target",
    )

    @api.depends("confidence")
    def _compute_risk_level(self):
        """Auto-compute risk level based on confidence."""
        for kr in self:
            if kr.confidence is None:
                kr.risk_level = "medium"
            elif kr.confidence < 25:
                kr.risk_level = "critical"
            elif kr.confidence < 40:
                kr.risk_level = "high"
            elif kr.confidence < 70:
                kr.risk_level = "medium"
            else:
                kr.risk_level = "low"

    @api.depends("baseline_value", "target_value", "current_value", "direction")
    def _compute_progress_pct(self):
        """Calculate progress percentage toward target."""
        for kr in self:
            if kr.target_value == kr.baseline_value:
                kr.progress_pct = 100.0 if kr.current_value == kr.target_value else 0.0
                continue

            delta_target = kr.target_value - kr.baseline_value
            delta_current = kr.current_value - kr.baseline_value

            if kr.direction == "decrease":
                # For decrease, flip the calculation
                delta_target = kr.baseline_value - kr.target_value
                delta_current = kr.baseline_value - kr.current_value

            if delta_target != 0:
                kr.progress_pct = min(100.0, max(0.0, (delta_current / delta_target) * 100))
            else:
                kr.progress_pct = 0.0

    def action_record_score(self):
        """Open wizard to record a score snapshot."""
        return {
            "type": "ir.actions.act_window",
            "name": "Record Score",
            "res_model": "okr.kr.score.snapshot",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_key_result_id": self.id,
                "default_score": self.status_score,
                "default_confidence": self.confidence,
            },
        }

    def action_create_risk(self):
        """Create a risk entry for this KR."""
        return {
            "type": "ir.actions.act_window",
            "name": "Create Risk",
            "res_model": "okr.risk",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_key_result_id": self.id,
                "default_name": f"Risk on {self.name}",
            },
        }

    @api.onchange("confidence")
    def _onchange_confidence_warning(self):
        """Warn when confidence drops below threshold."""
        if self.confidence and self.confidence < 40:
            return {
                "warning": {
                    "title": "Low Confidence Alert",
                    "message": (
                        f"Confidence is below 40%. Consider creating a risk "
                        f"entry and mitigation plan for '{self.name}'."
                    ),
                }
            }
