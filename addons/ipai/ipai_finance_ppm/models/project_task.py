# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    """Extend project.task to link to Finance PPM logframe and BIR schedule"""

    _inherit = "project.task"

    # ===============================
    # Finance Kanban State Fields
    # ===============================
    finance_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "In Progress"),
            ("review", "Under Review"),
            ("done", "Closed"),
        ],
        string="Kanban State",
        default="draft",
        tracking=True,
        group_expand="_read_group_finance_state",
        help="Finance workflow state for Kanban board visualization",
    )

    # Toggle Feature Fields
    is_closing_task = fields.Boolean(
        string="Is Month-End Task",
        default=False,
        tracking=True,
        help="Mark this task as part of month-end close workflow",
    )

    is_compliance_task = fields.Boolean(
        string="Is Tax Compliance",
        default=False,
        tracking=True,
        help="Mark this task as tax compliance related (BIR, VAT, etc.)",
    )

    # Scheduling & Alert Fields
    deadline_date = fields.Date(
        string="Statutory Deadline",
        help="Official deadline for regulatory compliance",
    )

    alert_days_before = fields.Integer(
        string="Alert Days Before",
        default=3,
        help="Number of days before deadline to send alert notification",
    )

    recurrence_rule_id = fields.Many2one(
        "finance.recurrence.rule",
        string="Recurrence Pattern",
        help="Link to recurrence rule for automated task regeneration",
    )

    # ===============================
    # Finance-specific fields
    # ===============================
    finance_code = fields.Char(
        string="Finance Code", help="Employee code like RIM, BOM, CKVC"
    )

    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer/Consulted",
        help="Person responsible for reviewing the task",
    )

    approver_id = fields.Many2one(
        "res.users",
        string="Approver/Accountable",
        help="Person responsible for final approval",
    )

    finance_deadline_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        string="Finance Deadline Type",
    )

    # Link to finance person directory
    finance_person_id = fields.Many2one("ipai.finance.person", string="Finance Person")

    # Duration fields for finance workflow
    prep_duration = fields.Float(string="Prep Duration (Days)")
    review_duration = fields.Float(string="Review Duration (Days)")
    approval_duration = fields.Float(string="Approval Duration (Days)")

    # Finance categories
    finance_category = fields.Selection(
        [
            ("foundation_corp", "Foundation & Corp"),
            ("revenue_wip", "Revenue/WIP"),
            ("vat_tax", "VAT & Tax Reporting"),
            ("working_capital", "Working Capital"),
            ("compliance", "Compliance"),
            ("administrative", "Administrative"),
        ],
        string="Finance Category",
    )

    finance_logframe_id = fields.Many2one(
        "ipai.finance.logframe",
        string="Logframe Entry",
        help="Link to Finance Logical Framework objective",
    )

    bir_schedule_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR Filing Schedule",
    )

    # Generator tracking fields (for seed-based task generation)
    x_cycle_key = fields.Char(
        string="Cycle Instance Key",
        index=True,
        help="Instance key: MONTH_END_CLOSE|2025-11 (for generator idempotency)",
    )

    x_task_template_code = fields.Char(
        string="Task Template Code",
        index=True,
        help="Template code: CT_PAYROLL_PERSONNEL (from seed JSON)",
    )

    x_step_code = fields.Char(
        string="Step Code",
        index=True,
        help="Step code: PREP|REVIEW|APPROVAL (from seed JSON)",
    )

    x_external_key = fields.Char(
        string="External Deduplication Key",
        index=True,
        help="Full external key: CYCLE_KEY|TEMPLATE_CODE|STEP_CODE (prevents duplicates)",
    )

    x_seed_hash = fields.Char(
        string="Template Seed Hash",
        index=True,
        help="SHA256 hash of template for change detection",
    )

    x_obsolete = fields.Boolean(
        string="Obsolete",
        default=False,
        index=True,
        help="Marked obsolete by generator (template removed from seed)",
    )

    # Computed fields for dashboard visibility
    is_finance_ppm = fields.Boolean(
        compute="_compute_is_finance_ppm", store=True, string="Is Finance PPM Task"
    )

    def _compute_is_finance_ppm(self):
        for task in self:
            task.is_finance_ppm = bool(
                task.finance_logframe_id
                or task.bir_schedule_id
                or task.x_external_key  # Include generator-created tasks
            )

    @api.model
    def _read_group_finance_state(self, stages, domain):
        """
        Ensure all finance_state values are shown in Kanban view.
        This method is called by group_expand attribute.
        """
        return [
            ("draft", "Draft"),
            ("active", "In Progress"),
            ("review", "Under Review"),
            ("done", "Closed"),
        ]

    def action_set_draft(self):
        """Set task to draft state"""
        self.write({"finance_state": "draft"})

    def action_set_active(self):
        """Set task to active/in-progress state"""
        self.write({"finance_state": "active"})

    def action_set_review(self):
        """Set task to review state"""
        self.write({"finance_state": "review"})

    def action_set_done(self):
        """Set task to done/closed state"""
        self.write({"finance_state": "done"})

    def toggle_is_closing_task(self):
        """Toggle the month-end close task flag"""
        for task in self:
            task.is_closing_task = not task.is_closing_task

    def toggle_is_compliance_task(self):
        """Toggle the tax compliance task flag"""
        for task in self:
            task.is_compliance_task = not task.is_compliance_task
