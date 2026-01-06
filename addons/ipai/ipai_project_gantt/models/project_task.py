# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ipai_planned_start = fields.Datetime(
        string="Planned Start",
        index=True,
        tracking=True,
        help="Start date/time for IPAI Gantt view planning.",
    )
    ipai_planned_end = fields.Datetime(
        string="Planned End",
        index=True,
        tracking=True,
        help="End date/time for IPAI Gantt view planning.",
    )
    ipai_planned_duration = fields.Float(
        string="Planned Duration (days)",
        compute="_compute_ipai_planned_duration",
        store=True,
        help="Computed duration in days between planned start and end.",
    )

    @api.depends("ipai_planned_start", "ipai_planned_end")
    def _compute_ipai_planned_duration(self):
        for task in self:
            if task.ipai_planned_start and task.ipai_planned_end:
                delta = task.ipai_planned_end - task.ipai_planned_start
                task.ipai_planned_duration = delta.total_seconds() / 86400.0
            else:
                task.ipai_planned_duration = 0.0

    @api.onchange("date_deadline")
    def _onchange_deadline_default_end(self):
        """Auto-populate planning dates from deadline if not set."""
        for task in self:
            if task.date_deadline and not task.ipai_planned_end:
                # Set end to end-of-day on deadline
                deadline_str = str(task.date_deadline) + " 23:59:59"
                task.ipai_planned_end = fields.Datetime.to_datetime(deadline_str)
            if task.ipai_planned_end and not task.ipai_planned_start:
                # Default 2-day window before end
                task.ipai_planned_start = task.ipai_planned_end - timedelta(days=2)

    @api.onchange("ipai_planned_start")
    def _onchange_planned_start(self):
        """Auto-set end date if start is set but end is not."""
        for task in self:
            if task.ipai_planned_start and not task.ipai_planned_end:
                # Default 3-day task duration
                task.ipai_planned_end = task.ipai_planned_start + timedelta(days=3)

    def action_set_planned_dates_from_deadline(self):
        """Batch action to set planned dates from deadline for selected tasks."""
        for task in self:
            if task.date_deadline:
                deadline_str = str(task.date_deadline) + " 23:59:59"
                task.ipai_planned_end = fields.Datetime.to_datetime(deadline_str)
                task.ipai_planned_start = task.ipai_planned_end - timedelta(days=2)
        return True
