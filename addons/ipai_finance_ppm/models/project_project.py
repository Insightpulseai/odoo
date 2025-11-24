# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class ProjectProject(models.Model):
    """Extend project.project with automated health status (RAG).

    The computation follows Traffic Light logic:
    - RED: Project deadline has passed or tasks are overdue by more than 2 days.
    - AMBER: Deadline within 3 days or active tasks lack an assignee.
    - GREEN: No risks detected.
    """

    _inherit = "project.project"

    health_status = fields.Selection(
        selection=[("green", "On Track"), ("amber", "At Risk"), ("red", "Critical")],
        string="Health Status",
        compute="_compute_health_status",
        store=True,
        help="Automated RAG status based on deadlines, overdue work, and task ownership.",
    )

    @api.depends(
        "date",
        "task_ids.date_deadline",
        "task_ids.stage_id.fold",
        "task_ids.user_ids",
    )
    def _compute_health_status(self):
        today = fields.Date.context_today(self)
        danger_threshold = today - timedelta(days=2)
        warning_threshold = today + timedelta(days=3)

        for project in self:
            status = "green"

            if project.date and project.date < today:
                status = "red"

            if status != "red":
                overdue_tasks = project.task_ids.filtered(
                    lambda task: task.date_deadline
                    and task.date_deadline < danger_threshold
                    and not task.stage_id.fold
                )
                if overdue_tasks:
                    status = "red"

            if status != "red":
                warning_deadline = project.date and project.date <= warning_threshold
                unassigned_active_tasks = project.task_ids.filtered(
                    lambda task: not task.stage_id.fold and not task.user_ids
                )
                if warning_deadline or unassigned_active_tasks:
                    status = "amber"

            project.health_status = status
