from odoo import fields, models


class PpmResourceRole(models.Model):
    _name = "ppm.resource.role"
    _description = "PPM Resource Role"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)


class PpmResourceAllocation(models.Model):
    _name = "ppm.resource.allocation"
    _description = "PPM Resource Allocation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    task_id = fields.Many2one("project.task", ondelete="set null", index=True)
    user_id = fields.Many2one("res.users", required=True, tracking=True)
    role_id = fields.Many2one("ppm.resource.role")

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    allocation_percent = fields.Float(required=True, help="0-100%")

    cost_rate = fields.Float()
    bill_rate = fields.Float()
