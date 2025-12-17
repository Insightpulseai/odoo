# -*- coding: utf-8 -*-
from odoo import models, fields

class ProjectTask(models.Model):
    """Extend project.task to link to Finance PPM logframe and BIR schedule"""
    _inherit = "project.task"

    finance_logframe_id = fields.Many2one(
        "ipai.finance.logframe",
        string="Logframe Entry",
        help="Link to Finance Logical Framework objective"
    )

    bir_schedule_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR Filing Schedule"
    )

    # Generator tracking fields (for seed-based task generation)
    x_cycle_key = fields.Char(
        string='Cycle Instance Key',
        index=True,
        help='Instance key: MONTH_END_CLOSE|2025-11 (for generator idempotency)'
    )

    x_task_template_code = fields.Char(
        string='Task Template Code',
        index=True,
        help='Template code: CT_PAYROLL_PERSONNEL (from seed JSON)'
    )

    x_step_code = fields.Char(
        string='Step Code',
        index=True,
        help='Step code: PREP|REVIEW|APPROVAL (from seed JSON)'
    )

    x_external_key = fields.Char(
        string='External Deduplication Key',
        index=True,
        help='Full external key: CYCLE_KEY|TEMPLATE_CODE|STEP_CODE (prevents duplicates)'
    )

    x_seed_hash = fields.Char(
        string='Template Seed Hash',
        index=True,
        help='SHA256 hash of template for change detection'
    )

    x_obsolete = fields.Boolean(
        string='Obsolete',
        default=False,
        index=True,
        help='Marked obsolete by generator (template removed from seed)'
    )

    # Computed fields for dashboard visibility
    is_finance_ppm = fields.Boolean(
        compute="_compute_is_finance_ppm",
        store=True,
        string="Is Finance PPM Task"
    )

    def _compute_is_finance_ppm(self):
        for task in self:
            task.is_finance_ppm = bool(
                task.finance_logframe_id or
                task.bir_schedule_id or
                task.x_external_key  # Include generator-created tasks
            )
