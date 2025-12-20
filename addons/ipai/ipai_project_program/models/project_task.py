# -*- coding: utf-8 -*-
"""Project task extensions for finance workflow tracking."""
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Activity/workflow type
    activity_type = fields.Selection(
        [
            ("prep", "Preparation"),
            ("review", "Review"),
            ("approve", "Approval"),
            ("file", "Filing"),
        ],
        string="Activity Type",
        index=True,
        help="Type of activity in the workflow (Prep/Review/Approve/File)",
    )

    # Role-based assignment
    role_code = fields.Char(
        string="Role Code",
        index=True,
        help="Directory code for role-based assignment (e.g., RIM, BOM, CKVC)",
    )

    # BIR-specific fields (used by ipai_finance_bir_compliance)
    bir_form = fields.Char(
        string="BIR Form",
        index=True,
        help="BIR form number (e.g., 1601-C, 2550M)",
    )
    period_covered = fields.Char(
        string="Period Covered",
        index=True,
        help="Period covered by this filing (e.g., Dec 2025)",
    )
    target_date = fields.Date(
        string="Target Date",
        index=True,
        help="Computed target date for this task step",
    )
