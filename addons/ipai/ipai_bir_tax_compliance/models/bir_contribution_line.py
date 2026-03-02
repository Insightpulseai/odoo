from odoo import fields, models


class BirContributionLine(models.Model):
    _name = "ipai.bir.contribution.line"
    _description = "BIR Contribution Line"
    _order = "range_from"

    table_id = fields.Many2one(
        "ipai.bir.contribution.table",
        string="Contribution Table",
        required=True,
        ondelete="cascade",
    )
    range_from = fields.Float(
        string="Compensation From",
        required=True,
        help="Lower bound of compensation range.",
    )
    range_to = fields.Float(
        string="Compensation To",
        required=True,
        help="Upper bound of compensation range.",
    )
    employee_share = fields.Float(
        string="Employee Share",
        required=True,
        help="Employee contribution amount for this bracket.",
    )
    employer_share = fields.Float(
        string="Employer Share",
        required=True,
        help="Employer contribution amount for this bracket.",
    )
