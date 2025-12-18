# -*- coding: utf-8 -*-
"""Project extensions for Program + Implementation Module hierarchy."""
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    # Hierarchy fields
    parent_id = fields.Many2one(
        "project.project",
        string="Parent Program",
        index=True,
        ondelete="restrict",
        help="Parent program project for Implementation Modules",
    )
    child_ids = fields.One2many(
        "project.project",
        "parent_id",
        string="Implementation Modules",
    )

    # Program/IM identification
    im_code = fields.Char(
        string="IM Code",
        index=True,
        help="Implementation Module code (IM1, IM2, ...)",
    )
    program_code = fields.Char(
        string="Program Code",
        index=True,
        help="Program identifier e.g., PRJ-2025-002",
    )
    program_type = fields.Selection(
        [
            ("finance_ppm", "Finance PPM"),
            ("bir", "BIR Compliance"),
            ("hybrid", "Hybrid"),
        ],
        string="Program Type",
        default="hybrid",
        index=True,
    )
    is_program = fields.Boolean(
        string="Is Program",
        default=False,
        index=True,
        help="True for parent roll-up Program project",
    )

    # Computed roll-up fields
    im_count = fields.Integer(
        string="IM Count",
        compute="_compute_im_rollups",
        store=False,
    )
    im_task_count = fields.Integer(
        string="IM Task Count",
        compute="_compute_im_rollups",
        store=False,
    )

    @api.depends("child_ids")
    def _compute_im_rollups(self):
        """Compute roll-up counts for program projects."""
        Task = self.env["project.task"].sudo()
        for rec in self:
            rec.im_count = len(rec.child_ids)
            if rec.child_ids:
                rec.im_task_count = Task.search_count(
                    [("project_id", "in", rec.child_ids.ids)]
                )
            else:
                rec.im_task_count = 0

    def action_view_child_projects(self):
        """Open list of Implementation Module projects."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Implementation Modules",
            "res_model": "project.project",
            "view_mode": "kanban,tree,form",
            "domain": [("parent_id", "=", self.id)],
            "context": {"default_parent_id": self.id},
        }

    def action_view_child_tasks(self):
        """Open list of tasks across all Implementation Modules."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "IM Tasks",
            "res_model": "project.task",
            "view_mode": "kanban,tree,form",
            "domain": [("project_id", "in", self.child_ids.ids)],
            "context": {},
        }
