from odoo import fields, models


class BirContributionTable(models.Model):
    _name = "ipai.bir.contribution.table"
    _description = "BIR Contribution Table (SSS / PhilHealth / Pag-IBIG)"
    _order = "effective_date desc, name"

    name = fields.Char(required=True)
    contribution_type = fields.Selection(
        selection=[
            ("sss", "SSS"),
            ("philhealth", "PhilHealth"),
            ("pagibig", "Pag-IBIG/HDMF"),
        ],
        string="Contribution Type",
        required=True,
    )
    effective_date = fields.Date(required=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many(
        "ipai.bir.contribution.line",
        "table_id",
        string="Contribution Lines",
    )
