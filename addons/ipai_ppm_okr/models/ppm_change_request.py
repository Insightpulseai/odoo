from odoo import fields, models


class PpmChangeRequest(models.Model):
    _name = "ppm.change.request"
    _description = "PPM Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    title = fields.Char(required=True, tracking=True)
    description = fields.Text()

    requested_by_user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, tracking=True
    )
    requested_at = fields.Datetime(default=fields.Datetime.now)

    impact_scope = fields.Text()
    impact_cost = fields.Float()
    impact_schedule_days = fields.Integer()

    decision = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        tracking=True,
    )

    decided_by_user_id = fields.Many2one("res.users")
    decided_at = fields.Datetime()
