from odoo import api, fields, models


class PpmPortfolio(models.Model):
    _name = "ppm.portfolio"
    _description = "PPM Portfolio"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
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

    strategic_theme = fields.Char()
    target_value_statement = fields.Text()

    program_ids = fields.One2many("ppm.program", "portfolio_id")
    project_meta_ids = fields.One2many("ppm.project.meta", "portfolio_id")
    okr_objective_ids = fields.One2many("okr.objective", "portfolio_id")

    _sql_constraints = [
        (
            "ppm_portfolio_code_uniq",
            "unique(code, company_id)",
            "Portfolio code must be unique per company.",
        ),
    ]
