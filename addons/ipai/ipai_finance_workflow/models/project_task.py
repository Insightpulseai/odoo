# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import fields, models


class ProjectTask(models.Model):
    """Extend project tasks with finance workflow fields."""

    _inherit = "project.task"

    # Finance workflow fields
    finance_stage = fields.Selection(
        [
            ("prep", "Preparation"),
            ("review", "Review"),
            ("approve", "Approval"),
            ("execute", "Execute / File / Pay"),
            ("close", "Closed / Archived"),
        ],
        string="Finance Stage",
        help="Normalized finance workflow stage.",
    )
    preparer_id = fields.Many2one(
        "res.users",
        string="Preparer",
        help="User responsible for preparation.",
    )
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        help="User responsible for review.",
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        help="User responsible for approval.",
    )
    preparer_role_id = fields.Many2one(
        "ipai.finance.role",
        string="Preparer Role",
        help="Finance role for preparation.",
    )
    reviewer_role_id = fields.Many2one(
        "ipai.finance.role",
        string="Reviewer Role",
        help="Finance role for review.",
    )
    approver_role_id = fields.Many2one(
        "ipai.finance.role",
        string="Approver Role",
        help="Finance role for approval.",
    )
    # Time estimates
    prep_hours = fields.Float(
        string="Prep Time (hrs)",
        help="Estimated preparation time in hours.",
    )
    review_hours = fields.Float(
        string="Review Time (hrs)",
        help="Estimated review time in hours.",
    )
    approval_hours = fields.Float(
        string="Approval Time (hrs)",
        help="Estimated approval time in hours.",
    )
    # Workflow type
    finance_workflow_type = fields.Selection(
        [
            ("month_end", "Month-End Close"),
            ("bir", "BIR Returns"),
            ("other", "Other Finance"),
        ],
        string="Workflow Type",
        help="Type of finance workflow.",
    )
    # BIR-specific
    bir_form_code = fields.Char(
        string="BIR Form Code",
        help="BIR form number (e.g., 1601-C, 2550M)",
    )
    bir_due_date = fields.Date(
        string="BIR Due Date",
        help="Statutory due date for BIR filing.",
    )
    # Month-end specific
    closing_period = fields.Char(
        string="Closing Period",
        help="Month/year being closed (e.g., Dec 2025)",
    )


class ProjectTaskType(models.Model):
    """Extend task types with finance workflow metadata."""

    _inherit = "project.task.type"

    is_finance_stage = fields.Boolean(
        string="Finance Stage",
        default=False,
        help="Mark as a normalized finance workflow stage.",
    )
    finance_stage_code = fields.Selection(
        [
            ("prep", "PREP"),
            ("review", "REVIEW"),
            ("approve", "APPROVE"),
            ("execute", "EXECUTE"),
            ("close", "CLOSE"),
        ],
        string="Finance Stage Code",
        help="Canonical stage code for finance workflows.",
    )
