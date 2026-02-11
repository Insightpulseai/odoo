from odoo import fields, models


class PpmWorkstream(models.Model):
    _name = "ppm.workstream"
    _description = "PPM Workstream"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    name = fields.Char(required=True, tracking=True)
    lead_user_id = fields.Many2one("res.users", tracking=True)
    sequence = fields.Integer(default=10)
    start_date = fields.Date()
    end_date = fields.Date()

    epic_ids = fields.One2many("ppm.epic", "workstream_id")
