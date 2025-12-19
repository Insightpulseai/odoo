# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class GenerateIMProjectsWizard(models.TransientModel):
    _name = "ipai.generate.im.projects.wizard"
    _description = "Generate IM1/IM2 Projects and Tasks"

    project_id = fields.Many2one("project.project", required=True)
    create_children = fields.Boolean(default=True)
    create_month_end_tasks = fields.Boolean(default=True)
    create_bir_tasks = fields.Boolean(default=True)

    def action_generate(self):
        self.ensure_one()
        root = self.project_id

        if not root:
            raise UserError(_("No root project selected."))

        # Create child projects (IM1/IM2)
        im1 = root._ipai_find_or_create_child("IM1", "IM1 Month-End Close")
        im2 = root._ipai_find_or_create_child("IM2", "IM2 Tax & BIR Compliance")

        # Generate tasks
        if self.create_month_end_tasks:
            im1.ipai_generate_tasks_from_templates()
        if self.create_bir_tasks:
            im2.ipai_generate_tasks_from_bir_schedule()

        # Mark root
        root.ipai_finance_enabled = True

        return {
            "type": "ir.actions.act_window",
            "name": _("IM Projects"),
            "res_model": "project.project",
            "view_mode": "tree,form",
            "domain": [("id", "in", [im1.id, im2.id])],
        }
