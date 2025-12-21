# -*- coding: utf-8 -*-
"""
A1 Task Template

Reusable task definition with steps (prep/review/approval).
Maps to close.task.template in the close orchestration module.
"""
from odoo import api, fields, models


class A1Template(models.Model):
    """
    Task template defining reusable task structure.

    Each template has steps (PREP, REVIEW, APPROVAL) with role assignments.
    """

    _name = "a1.template"
    _description = "A1 Task Template"
    _order = "sequence, code"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        ("code_uniq", "unique(code, company_id)", "Template code must be unique per company."),
    ]

    # Core fields
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        tracking=True,
        help="Unique identifier like 'VAT_REPORT', 'BANK_RECON'",
    )
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Hierarchy
    workstream_id = fields.Many2one(
        "a1.workstream",
        string="Workstream",
        required=True,
        ondelete="cascade",
        index=True,
    )
    phase_code = fields.Char(
        string="Phase Code",
        related="workstream_id.phase_code",
        store=True,
    )

    # Role assignments (codes for flexibility)
    owner_role = fields.Char(
        string="Owner Role",
        required=True,
        help="Role code for task owner (e.g., 'RIM', 'CKVC')",
    )
    reviewer_role = fields.Char(
        string="Reviewer Role",
        help="Role code for reviewer",
    )
    approver_role = fields.Char(
        string="Approver Role",
        help="Role code for approver",
    )

    # Effort estimation (in days)
    prep_days = fields.Float(
        string="Prep Days",
        default=1.0,
        help="Estimated effort for preparation phase",
    )
    review_days = fields.Float(
        string="Review Days",
        default=0.5,
        help="Estimated effort for review phase",
    )
    approval_days = fields.Float(
        string="Approval Days",
        default=0.5,
        help="Estimated effort for approval phase",
    )
    total_days = fields.Float(
        string="Total Days",
        compute="_compute_total_days",
        store=True,
    )

    # Steps (one2many for flexibility)
    step_ids = fields.One2many(
        "a1.template.step",
        "template_id",
        string="Steps",
    )

    # Checklist items
    checklist_ids = fields.One2many(
        "a1.template.checklist",
        "template_id",
        string="Checklist Items",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to close orchestration
    close_template_id = fields.Many2one(
        "close.task.template",
        string="Close Template",
        help="Linked template in Close Orchestration module",
    )

    # Description
    description = fields.Html(
        string="Description",
        help="Detailed task instructions",
    )

    @api.depends("prep_days", "review_days", "approval_days")
    def _compute_total_days(self):
        for tpl in self:
            tpl.total_days = (
                (tpl.prep_days or 0) +
                (tpl.review_days or 0) +
                (tpl.approval_days or 0)
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create default steps if none provided."""
        records = super().create(vals_list)
        for rec in records:
            if not rec.step_ids:
                rec._create_default_steps()
        return records

    def _create_default_steps(self):
        """Create default PREP/REVIEW/APPROVAL steps."""
        Step = self.env["a1.template.step"]
        Step.create([
            {
                "template_id": self.id,
                "code": "PREP",
                "name": "Preparation",
                "sequence": 10,
                "assignee_role": self.owner_role,
                "effort_days": self.prep_days,
            },
            {
                "template_id": self.id,
                "code": "REVIEW",
                "name": "Review",
                "sequence": 20,
                "assignee_role": self.reviewer_role or self.owner_role,
                "effort_days": self.review_days,
            },
            {
                "template_id": self.id,
                "code": "APPROVAL",
                "name": "Approval",
                "sequence": 30,
                "assignee_role": self.approver_role or self.reviewer_role or self.owner_role,
                "effort_days": self.approval_days,
            },
        ])


class A1TemplateStep(models.Model):
    """
    Step within a task template.

    Steps define the workflow stages (PREP → REVIEW → APPROVAL).
    """

    _name = "a1.template.step"
    _description = "A1 Template Step"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "a1.template",
        string="Template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Step code (PREP, REVIEW, APPROVAL)",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Assignment
    assignee_role = fields.Char(
        string="Assignee Role",
        help="Role code for step assignee",
    )

    # Effort
    effort_days = fields.Float(
        string="Effort (Days)",
        default=1.0,
    )

    # Deadline offset
    deadline_offset_days = fields.Integer(
        string="Deadline Offset",
        default=0,
        help="Days before period end (negative = before, positive = after)",
    )


class A1TemplateChecklist(models.Model):
    """
    Checklist item template.

    Defines validation/verification items for a task template.
    """

    _name = "a1.template.checklist"
    _description = "A1 Template Checklist Item"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "a1.template",
        string="Template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Unique item code within template",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Item type
    item_type = fields.Selection([
        ("check", "Checkbox"),
        ("input", "Input Value"),
        ("upload", "File Upload"),
        ("approve", "Approval Sign-off"),
    ], string="Type", default="check", required=True)

    # Required
    is_required = fields.Boolean(
        string="Required",
        default=True,
        help="Must be completed before task can progress",
    )

    # Instructions
    instructions = fields.Text(string="Instructions")
