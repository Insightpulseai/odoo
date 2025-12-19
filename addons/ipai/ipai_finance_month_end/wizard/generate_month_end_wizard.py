# -*- coding: utf-8 -*-
"""Wizard to generate month-end tasks."""
from odoo import _, fields, models


class IPAIGenerateMonthEndWizard(models.TransientModel):
    _name = "ipai.generate.month.end.wizard"
    _description = "Generate Month-End Tasks"

    program_project_id = fields.Many2one(
        "project.project",
        string="Program",
        required=True,
        domain=[("is_program", "=", True)],
        help="Select the parent Program project",
    )
    anchor_date = fields.Date(
        string="Anchor Date",
        required=True,
        help="Anchor date for offsets (e.g., month-end close date)",
    )
    dry_run = fields.Boolean(
        string="Dry Run",
        default=False,
        help="If checked, only count tasks that would be created",
    )

    def action_generate(self):
        """Generate month-end tasks."""
        self.ensure_one()
        created = self.env["ipai.month.end.generator"].generate(
            self.program_project_id,
            self.anchor_date,
            templates=None,
            dry_run=self.dry_run,
        )
        msg = (
            _("Would create %s tasks (dry run).") % created
            if self.dry_run
            else _("Created %s tasks.") % created
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Month-End Generation"),
                "message": msg,
                "sticky": False,
                "type": "success" if created > 0 else "warning",
            },
        }
