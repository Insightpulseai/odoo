# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    """Extend project.project for OKR Objective tracking.

    Maps OKR Objectives to Odoo CE projects:
    - x_is_okr: Flag to identify OKR projects
    - x_period_start/end: OKR period dates
    - x_overall_score: Computed from KR tasks
    - x_confidence: Overall confidence level
    - PMBOK alignment notes fields
    """

    _inherit = "project.project"

    # ===============================
    # Program/Portfolio Hierarchy
    # ===============================
    x_is_program = fields.Boolean(
        string="Is Program",
        default=False,
        tracking=True,
        help="Mark this project as a Program (container for sub-projects)",
    )

    x_program_id = fields.Many2one(
        "project.project",
        string="Program",
        domain="[('x_is_program', '=', True)]",
        tracking=True,
        help="Parent program this project belongs to",
    )

    x_child_project_ids = fields.One2many(
        "project.project",
        "x_program_id",
        string="Sub-Projects",
    )

    x_child_project_count = fields.Integer(
        string="Sub-Projects",
        compute="_compute_child_project_count",
    )

    @api.depends("x_child_project_ids")
    def _compute_child_project_count(self):
        for project in self:
            project.x_child_project_count = len(project.x_child_project_ids)

    # ===============================
    # OKR Objective Fields
    # ===============================
    x_is_okr = fields.Boolean(
        string="Is OKR Objective",
        default=False,
        tracking=True,
        help="Mark this project as an OKR Objective container",
    )

    x_period_start = fields.Date(
        string="OKR Period Start",
        tracking=True,
        help="Start of the OKR period (e.g., Q1 start)",
    )

    x_period_end = fields.Date(
        string="OKR Period End",
        tracking=True,
        help="End of the OKR period (e.g., Q1 end)",
    )

    x_overall_score = fields.Float(
        string="Overall Score (0-1.0)",
        digits=(3, 2),
        compute="_compute_okr_score",
        store=True,
        help="Average score from all Key Result tasks",
    )

    x_confidence = fields.Integer(
        string="Confidence (0-100)",
        default=50,
        tracking=True,
        help="Overall confidence in achieving this objective",
    )

    x_okr_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="OKR Status",
        default="draft",
        tracking=True,
    )

    # ===============================
    # PMBOK Alignment Notes
    # ===============================
    x_scope_notes = fields.Text(
        string="Scope Notes",
        help="PMBOK scope considerations",
    )

    x_schedule_notes = fields.Text(
        string="Schedule Notes",
        help="PMBOK schedule considerations",
    )

    x_cost_notes = fields.Text(
        string="Cost Notes",
        help="PMBOK cost considerations",
    )

    x_quality_notes = fields.Text(
        string="Quality Notes",
        help="PMBOK quality considerations",
    )

    x_stakeholder_notes = fields.Text(
        string="Stakeholder Notes",
        help="Key stakeholders and communication approach",
    )

    x_communication_cadence = fields.Char(
        string="Communication Cadence",
        default="Weekly Dashboard",
        help="How often this objective is reviewed",
    )

    # ===============================
    # Computed Fields
    # ===============================
    x_kr_count = fields.Integer(
        string="Key Results",
        compute="_compute_kr_stats",
        help="Number of Key Result tasks",
    )

    x_kr_at_risk = fields.Integer(
        string="KRs at Risk",
        compute="_compute_kr_stats",
        help="Key Results with confidence < 40%",
    )

    @api.depends("task_ids.x_is_kr", "task_ids.x_kr_score")
    def _compute_okr_score(self):
        """Compute average score from Key Result tasks."""
        for project in self:
            if not project.x_is_okr:
                project.x_overall_score = 0.0
                continue
            kr_tasks = project.task_ids.filtered(lambda t: t.x_is_kr)
            scores = [t.x_kr_score for t in kr_tasks if t.x_kr_score is not None]
            project.x_overall_score = sum(scores) / len(scores) if scores else 0.0

    @api.depends("task_ids.x_is_kr", "task_ids.x_kr_confidence")
    def _compute_kr_stats(self):
        """Compute KR statistics."""
        for project in self:
            kr_tasks = project.task_ids.filtered(lambda t: t.x_is_kr)
            project.x_kr_count = len(kr_tasks)
            project.x_kr_at_risk = len(
                kr_tasks.filtered(lambda t: t.x_kr_confidence and t.x_kr_confidence < 40)
            )

    def action_activate_okr(self):
        """Activate the OKR objective."""
        self.write({"x_okr_state": "active"})

    def action_close_okr(self):
        """Close the OKR objective."""
        self.write({"x_okr_state": "closed"})
