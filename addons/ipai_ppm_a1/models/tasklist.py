from odoo import api, fields, models


class IpaiPpmTaskList(models.Model):
    _name = "ipai.ppm.tasklist"
    _description = "Task List Run (Per Period)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, id desc"

    name = fields.Char(required=True, tracking=True)
    workstream_id = fields.Many2one(
        "ipai.workstream", required=True, ondelete="restrict", index=True
    )
    template_id = fields.Many2one(
        "ipai.ppm.template", required=True, ondelete="restrict", index=True
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("released", "Released"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    taskrun_ids = fields.One2many("ipai.ppm.taskrun", "tasklist_id")

    @api.model
    def create_from_template(self, template, period_start, period_end):
        """Create a task list from a template for a specific period."""
        tasklist = self.create(
            {
                "name": f"{template.workstream_id.code} | {template.code} | {period_end}",
                "workstream_id": template.workstream_id.id,
                "template_id": template.id,
                "period_start": period_start,
                "period_end": period_end,
                "status": "draft",
            }
        )
        runs = []
        for t in template.task_ids.sorted(key=lambda x: (x.sequence, x.id)):
            runs.append(
                (
                    0,
                    0,
                    {
                        "task_id": t.id,
                        "name": t.name,
                        "status": "todo",
                    },
                )
            )
        tasklist.write({"taskrun_ids": runs})
        return tasklist


class IpaiPpmTaskRun(models.Model):
    _name = "ipai.ppm.taskrun"
    _description = "Task Execution Instance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "tasklist_id, id"

    tasklist_id = fields.Many2one(
        "ipai.ppm.tasklist", required=True, ondelete="cascade", index=True
    )
    task_id = fields.Many2one(
        "ipai.ppm.task", required=True, ondelete="restrict", index=True
    )
    name = fields.Char(required=True)
    status = fields.Selection(
        [
            ("todo", "To Do"),
            ("doing", "Doing"),
            ("blocked", "Blocked"),
            ("done", "Done"),
            ("skipped", "Skipped"),
        ],
        default="todo",
        tracking=True,
    )
    assignee_id = fields.Many2one("res.users", ondelete="set null")
    approver_id = fields.Many2one("res.users", ondelete="set null")
    started_at = fields.Datetime()
    done_at = fields.Datetime()
