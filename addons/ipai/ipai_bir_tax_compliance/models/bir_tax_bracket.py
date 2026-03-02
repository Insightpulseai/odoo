from odoo import fields, models


class BirTaxBracket(models.Model):
    _name = "ipai.bir.tax.bracket"
    _description = "BIR Withholding Tax Bracket"
    _order = "range_from"

    table_id = fields.Many2one(
        "ipai.bir.tax.table",
        string="Tax Table",
        required=True,
        ondelete="cascade",
    )
    range_from = fields.Float(
        string="Compensation From",
        required=True,
        help="Lower bound of the compensation range (inclusive).",
    )
    range_to = fields.Float(
        string="Compensation To",
        required=True,
        help="Upper bound of the compensation range (inclusive). 0 means no upper limit.",
    )
    base_tax = fields.Float(
        string="Base Tax",
        help="Fixed tax amount for this bracket.",
    )
    excess_rate = fields.Float(
        string="Excess Rate",
        help="Percentage rate applied to excess over threshold (e.g. 0.20 for 20%%).",
    )
    excess_over = fields.Float(
        string="Excess Over",
        help="Threshold amount; the excess_rate is applied to (income - excess_over).",
    )
