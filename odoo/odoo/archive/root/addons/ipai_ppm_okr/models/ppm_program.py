from odoo import fields, models


class PpmProgram(models.Model):
    _name = "ppm.program"
    _description = "PPM Program"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    portfolio_id = fields.Many2one(
        "ppm.portfolio", required=True, ondelete="cascade", tracking=True
    )
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)
    owner_user_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, tracking=True
    )
    description = fields.Text()

    start_date = fields.Date()
    end_date = fields.Date()

    stage = fields.Selection(
        [
            ("idea", "Idea"),
            ("approved", "Approved"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("closed", "Closed"),
        ],
        default="idea",
        tracking=True,
    )

    rag_status = fields.Selection(
        [
            ("green", "Green"),
            ("amber", "Amber"),
            ("red", "Red"),
        ],
        default="green",
        tracking=True,
    )

    project_meta_ids = fields.One2many("ppm.project.meta", "program_id")
    okr_objective_ids = fields.One2many("okr.objective", "program_id")
