from odoo import fields, models


class CloseTaskCategory(models.Model):
    """Close task categories from TBWA month-end process."""

    _name = "close.task.category"
    _description = "Close Task Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    color = fields.Integer(default=0)

    # Default assignments
    default_prep_role = fields.Selection([
        ("rim", "RIM - Risk & Investments Manager"),
        ("jpal", "JPAL - GL Accountant"),
        ("bom", "BOM - Billing/Operations Manager"),
        ("jil", "JIL - Assets/Liabilities"),
        ("jap", "JAP - Payroll/Project"),
        ("jas", "JAS - Assets/Services"),
        ("rmqb", "RMQB - Employee Benefits"),
        ("jrmo", "JRMO - Revenue Management"),
    ], default="rim")

    default_review_role = fields.Selection([
        ("rim", "RIM"),
        ("sfm", "SFM - Senior Finance Manager"),
        ("ckvc", "CKVC - Controller"),
    ], default="rim")

    default_approve_role = fields.Selection([
        ("ckvc", "CKVC - Controller"),
        ("fd", "FD - Finance Director"),
    ], default="ckvc")

    # Timing defaults
    default_prep_days = fields.Integer(
        default=1,
        help="Default days for preparation phase"
    )
    default_review_days = fields.Integer(
        default=1,
        help="Default days for review phase"
    )
    default_approve_days = fields.Integer(
        default=1,
        help="Default days for approval phase"
    )

    # GL integration
    gl_account_ids = fields.Many2many(
        "account.account",
        string="Related GL Accounts",
        help="GL accounts typically affected by this category"
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("category_code_unique", "unique(code)", "Category code must be unique"),
    ]
