"""IPAI Tax Intelligence — Tax Compliance Pack model.

Compliance packs bundle versioned, country-scoped tax validation rules.
Each pack can be independently deployed, upgraded, and audited.

Constitution Principle 5: Local compliance is pack-based.
PH BIR is the first pack. Additional countries are future packs.
"""

from odoo import fields, models


class TaxCompliancePack(models.Model):
    _name = "tax.compliance.pack"
    _description = "Tax Compliance Pack"
    _order = "country_id, name, version desc"

    name = fields.Char(
        string="Pack Name",
        required=True,
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        help="Country for which this compliance pack applies.",
    )
    version = fields.Char(
        string="Version",
        required=True,
        default="1.0.0",
        help="Semantic version of this compliance pack (e.g. 1.0.0).",
    )
    description = fields.Text(
        string="Description",
        help="Overview of what tax laws, BIR regulations, or policies this pack enforces.",
    )
    rule_ids = fields.One2many(
        "tax.validation.rule",
        "compliance_pack_id",
        string="Validation Rules",
        help="All tax validation rules that belong to this compliance pack.",
    )
    rule_count = fields.Integer(
        string="Rule Count",
        compute="_compute_rule_count",
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
        help="Only active packs are applied during validation.",
    )
    effective_date = fields.Date(
        string="Effective Date",
        help="Date from which this version of the compliance pack is effective.",
    )
    reference = fields.Char(
        string="Legal Reference",
        help="Primary BIR Revenue Regulation, NIRC reference, or policy document.",
    )

    def _compute_rule_count(self):
        for pack in self:
            pack.rule_count = len(pack.rule_ids)

    _sql_constraints = [
        (
            "unique_country_version",
            "UNIQUE(country_id, version)",
            "Only one compliance pack per country per version is allowed.",
        ),
    ]
