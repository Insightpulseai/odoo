from odoo import fields, models


class OkrInitiative(models.Model):
    _name = "okr.initiative"
    _description = "OKR Initiative"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    objective_id = fields.Many2one("okr.objective", ondelete="cascade", index=True)
    key_result_id = fields.Many2one("okr.key.result", ondelete="cascade", index=True)

    project_id = fields.Many2one("project.project", ondelete="set null", index=True, tracking=True)
    task_id = fields.Many2one("project.task", ondelete="set null", index=True, tracking=True)

    owner_user_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()

    status = fields.Selection(
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
