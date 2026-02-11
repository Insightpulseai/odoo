from odoo import fields, models


class PpmEpic(models.Model):
    _name = "ppm.epic"
    _description = "PPM Epic"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    workstream_id = fields.Many2one("ppm.workstream", ondelete="set null")
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()

    stage = fields.Selection(
        [
            ("todo", "To Do"),
            ("doing", "Doing"),
            ("done", "Done"),
            ("blocked", "Blocked"),
        ],
        default="todo",
        tracking=True,
    )

    start_date = fields.Date()
    end_date = fields.Date()
    story_points = fields.Float()

    task_ids = fields.One2many("project.task", "ppm_epic_id")
