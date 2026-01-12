# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OkrKrTaskLink(models.Model):
    """Link between Key Results and WBS/Month-End Tasks.

    Maps KRs to specific work packages (project.task or custom task models)
    to track which activities contribute to achieving each KR.
    """

    _name = "okr.kr.task.link"
    _description = "KR Task Link"
    _order = "key_result_id, id"

    key_result_id = fields.Many2one(
        "okr.key.result",
        string="Key Result",
        required=True,
        ondelete="cascade",
    )
    task_model = fields.Char(
        string="Task Model",
        required=True,
        default="project.task",
        help="Technical model name (e.g., project.task, ipai.finance.task.template)",
    )
    task_id = fields.Integer(
        string="Task ID",
        required=True,
        help="ID of the linked task record",
    )
    role = fields.Selection(
        [
            ("preparer", "Preparer"),
            ("reviewer", "Reviewer"),
            ("approver", "Approver"),
            ("contributor", "Contributor"),
        ],
        string="Role",
        default="contributor",
        help="Role this task plays in achieving the KR",
    )

    # Denormalized fields for display
    task_name = fields.Char(
        string="Task Name",
        compute="_compute_task_info",
    )
    task_state = fields.Char(
        string="Task Status",
        compute="_compute_task_info",
    )

    # Reference field (Odoo 14+ dynamic reference)
    task_ref = fields.Reference(
        string="Task Reference",
        selection=[
            ("project.task", "Project Task"),
            ("ipai.finance.task.template", "Finance Task Template"),
        ],
        compute="_compute_task_ref",
    )

    @api.depends("task_model", "task_id")
    def _compute_task_info(self):
        """Fetch task name and state from the linked record."""
        for link in self:
            if link.task_model and link.task_id:
                try:
                    task = self.env[link.task_model].browse(link.task_id)
                    if task.exists():
                        link.task_name = task.display_name
                        link.task_state = getattr(task, "stage_id", False) and task.stage_id.name or ""
                    else:
                        link.task_name = f"[Deleted: {link.task_id}]"
                        link.task_state = ""
                except (KeyError, ValueError):
                    link.task_name = f"[Unknown model: {link.task_model}]"
                    link.task_state = ""
            else:
                link.task_name = ""
                link.task_state = ""

    @api.depends("task_model", "task_id")
    def _compute_task_ref(self):
        """Compute the reference field."""
        for link in self:
            if link.task_model and link.task_id:
                link.task_ref = f"{link.task_model},{link.task_id}"
            else:
                link.task_ref = False

    def action_open_task(self):
        """Open the linked task in a form view."""
        self.ensure_one()
        if self.task_model and self.task_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Linked Task",
                "res_model": self.task_model,
                "res_id": self.task_id,
                "view_mode": "form",
                "target": "current",
            }
