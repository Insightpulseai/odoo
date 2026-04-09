"""TaxPulse PH — Tax rule configuration model.

Constitution C4.4: multi-entity design — configurable tax profiles
per company without hard-coded single-entity assumptions.
"""

from odoo import api, fields, models


class TaxRuleConfig(models.Model):
    _name = "ipai.tax.rule.config"
    _description = "Tax Validation Rule Configuration"
    _order = "company_id, name"

    name = fields.Char(string="Rule Name", required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # VAT
    vat_rate = fields.Float(
        string="VAT Rate (%)",
        digits=(5, 2),
        default=12.0,
        help="Standard VAT rate (Philippine default: 12%)",
    )
    tolerance_amount = fields.Float(
        string="Tolerance (PHP)",
        digits=(16, 2),
        default=1.0,
        help="Acceptable rounding difference before flagging",
    )

    # Confidence thresholds
    confidence_error_threshold = fields.Float(
        string="Confidence Error Threshold",
        digits=(4, 2),
        default=0.85,
        help="Below this confidence, extraction is flagged as error",
    )
    confidence_warning_threshold = fields.Float(
        string="Confidence Warning Threshold",
        digits=(4, 2),
        default=0.95,
        help="Below this confidence, extraction gets a warning",
    )

    # Blocker behavior
    block_on_needs_review = fields.Boolean(
        string="Block Posting on Needs Review",
        default=True,
        help="If enabled, documents with needs_review status cannot be posted",
    )
    block_on_rejected = fields.Boolean(
        string="Block Posting on Rejected",
        default=True,
        help="If enabled, documents with rejected status cannot be posted",
    )

    # Auto-validation
    auto_validate_on_upload = fields.Boolean(
        string="Auto-validate on Upload",
        default=False,
        help="Automatically trigger validation when attachment is uploaded",
    )

    _sql_constraints = [
        (
            "unique_company_name",
            "UNIQUE(company_id, name)",
            "Rule name must be unique per company.",
        ),
    ]

    @api.model
    def get_config(self, company_id=None):
        """Get the active configuration for a company.

        Returns the first active config for the given company,
        or creates a default one if none exists.
        """
        company_id = company_id or self.env.company.id
        config = self.search(
            [("company_id", "=", company_id), ("active", "=", True)],
            limit=1,
        )
        if not config:
            config = self.create({
                "name": "Default PH Rules",
                "company_id": company_id,
            })
        return config
