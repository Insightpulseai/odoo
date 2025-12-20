# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectProject(models.Model):
    """
    Extend project.project with cycle code for closing task organization.
    """

    _inherit = "project.project"

    x_cycle_code = fields.Char(
        string="Cycle Code",
        index=True,
        help="Closing cycle code (e.g., MONTH_END_CLOSE, BIR_TAX_FILING)",
    )


class ProjectTask(models.Model):
    """
    Extend project.task with fields required by the closing task generator.

    These fields enable:
    - Idempotent task creation via external_key
    - Hierarchical organization (cycle → template → step)
    - Change detection via seed_hash
    - Obsolescence tracking
    """

    _inherit = "project.task"

    x_cycle_key = fields.Char(
        string="Cycle Key",
        index=True,
        help="Instance key (e.g., MONTH_END_CLOSE|2025-11)",
    )
    x_task_template_code = fields.Char(
        string="Task Template Code",
        index=True,
        help="Template identifier from seed (e.g., T_PAYROLL_PROCESSING)",
    )
    x_step_code = fields.Char(
        string="Step Code",
        index=True,
        help="Step within template (e.g., PREP, REVIEW, APPROVAL)",
    )
    x_external_key = fields.Char(
        string="External Key",
        index=True,
        help="Deterministic key for idempotent upserts",
    )
    x_seed_hash = fields.Char(
        string="Seed Hash",
        index=True,
        help="SHA256 hash of source seed payload for change detection",
    )
    x_obsolete = fields.Boolean(
        string="Obsolete",
        default=False,
        index=True,
        help="True if task was generated but is no longer in seed",
    )
