# -*- coding: utf-8 -*-
"""Wizard to generate BIR compliance tasks."""
from odoo import _, fields, models


class IPAIGenerateBIRTasksWizard(models.TransientModel):
    _name = "ipai.generate.bir.tasks.wizard"
    _description = "Generate BIR Tasks"

    program_project_id = fields.Many2one(
        "project.project",
        string="Program",
        required=True,
        domain=[("is_program", "=", True)],
        help="Select the parent Program project",
    )
    date_from = fields.Date(
        string="From Date",
        help="Filter BIR items with deadline >= this date",
    )
    date_to = fields.Date(
        string="To Date",
        help="Filter BIR items with deadline <= this date",
    )
    dry_run = fields.Boolean(
        string="Dry Run",
        default=False,
        help="If checked, only count tasks that would be created",
    )

    def action_generate(self):
        """Generate BIR tasks."""
        self.ensure_one()
        created = self.env["ipai.bir.generator"].generate(
            self.program_project_id,
            date_from=self.date_from,
            date_to=self.date_to,
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
                "title": _("BIR Task Generation"),
                "message": msg,
                "sticky": False,
                "type": "success" if created > 0 else "warning",
            },
        }
