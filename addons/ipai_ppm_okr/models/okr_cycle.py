from odoo import fields, models


class OkrCycle(models.Model):
    _name = "okr.cycle"
    _description = "OKR Cycle"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True, tracking=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        default="draft",
        tracking=True,
    )

    objective_ids = fields.One2many("okr.objective", "cycle_id")
