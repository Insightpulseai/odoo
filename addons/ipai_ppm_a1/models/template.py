from odoo import fields, models


class IpaiPpmTemplate(models.Model):
    _name = "ipai.ppm.template"
    _description = "PPM Template (Close/Compliance)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "workstream_id, sequence, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    workstream_id = fields.Many2one(
        "ipai.workstream", required=True, ondelete="cascade", index=True
    )
    period_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
            ("ad_hoc", "Ad Hoc"),
        ],
        default="monthly",
        required=True,
    )
    version = fields.Char(default="v1")
    is_active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    task_ids = fields.One2many("ipai.ppm.task", "template_id")

    _sql_constraints = [
        (
            "template_code_unique",
            "unique(code, workstream_id)",
            "Template code must be unique per workstream.",
        ),
    ]
