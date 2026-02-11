from odoo import fields, models


class PpmIssue(models.Model):
    _name = "ppm.issue"
    _description = "PPM Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    task_id = fields.Many2one("project.task", ondelete="set null", index=True)
    title = fields.Char(required=True, tracking=True)
    description = fields.Text()

    severity = fields.Selection(
        [
            ("low", "Low"),
            ("med", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="med",
        tracking=True,
    )

    owner_user_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    due_date = fields.Date()
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        default="open",
        tracking=True,
    )
