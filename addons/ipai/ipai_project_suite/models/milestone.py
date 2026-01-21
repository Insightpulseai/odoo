# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _name = "ipai.project.milestone"
    _description = "Project Milestone"
    _order = "date_target, sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Milestone Name", required=True, tracking=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id", store=True, readonly=True
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
        help="User responsible for this milestone.",
    )
    date_target = fields.Date(
        string="Target Date",
        tracking=True,
        help="Target date for milestone completion.",
    )
    date_actual = fields.Date(
        string="Actual Date", tracking=True, help="Actual completion date."
    )
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="State",
        default="open",
        tracking=True,
    )
    description = fields.Text(string="Description")
    task_ids = fields.One2many(
        "project.task",
        "ipai_milestone_id",
        string="Tasks",
        help="Tasks linked to this milestone.",
    )
    task_count = fields.Integer(compute="_compute_task_count", string="Task Count")
    progress = fields.Float(
        compute="_compute_progress",
        string="Progress (%)",
        help="Percentage of linked tasks completed.",
    )
    active = fields.Boolean(string="Active", default=True)

    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    def _compute_progress(self):
        for rec in self:
            tasks = rec.task_ids
            if not tasks:
                rec.progress = 0.0
            else:
                # Consider tasks in final stage as completed
                done_count = len(tasks.filtered(lambda t: t.stage_id.fold))
                rec.progress = (done_count / len(tasks)) * 100.0

    def action_mark_done(self):
        """Mark milestone as done."""
        self.write(
            {
                "state": "done",
                "date_actual": fields.Date.context_today(self),
            }
        )

    def action_reopen(self):
        """Reopen a cancelled or done milestone."""
        self.write(
            {
                "state": "open",
                "date_actual": False,
            }
        )

    def action_cancel(self):
        """Cancel the milestone."""
        self.write({"state": "cancel"})

    def action_view_tasks(self):
        """Open the list of linked tasks."""
        self.ensure_one()
        return {
            "name": f"Tasks for {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "list,form,kanban",
            "domain": [("ipai_milestone_id", "=", self.id)],
            "context": {
                "default_ipai_milestone_id": self.id,
                "default_project_id": self.project_id.id,
            },
        }
