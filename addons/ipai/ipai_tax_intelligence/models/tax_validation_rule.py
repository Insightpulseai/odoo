"""IPAI Tax Intelligence — Tax Validation Rule model.

Defines the rules evaluated during pre-posting tax validation.
Rules are structured, country/group-scoped, and pack-linkable.

Constitution Principle 5: Local compliance is pack-based.
Constitution Principle 7: MVP is explainable validation, not a full tax engine.
"""

from odoo import fields, models


class TaxValidationRule(models.Model):
    _name = "tax.validation.rule"
    _description = "Tax Validation Rule"
    _order = "sequence, id"

    name = fields.Char(
        string="Rule Name",
        required=True,
    )
    description = fields.Text(
        string="Description",
        help="Human-readable explanation of what this rule checks.",
    )
    rule_type = fields.Selection(
        [
            ("rate_check", "Rate Check"),
            ("jurisdiction_match", "Jurisdiction Match"),
            ("exemption_verify", "Exemption Verification"),
            ("withholding_check", "Withholding Check"),
            ("document_completeness", "Document Completeness"),
        ],
        string="Rule Type",
        required=True,
        default="rate_check",
    )
    applies_to = fields.Selection(
        [
            ("invoice", "Customer Invoice"),
            ("bill", "Vendor Bill"),
            ("expense", "Expense"),
            ("all", "All Documents"),
        ],
        string="Applies To",
        required=True,
        default="all",
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        help="Limit this rule to a specific country. Leave blank for global rules.",
    )
    tax_group_id = fields.Many2one(
        "account.tax.group",
        string="Tax Group",
        help="Scope this rule to a specific tax group.",
    )
    expression = fields.Text(
        string="Rule Expression",
        help=(
            "Optional structured expression or reference key for the rule logic. "
            "Used by validators to identify which check to execute."
        ),
    )
    severity = fields.Selection(
        [
            ("warning", "Warning"),
            ("blocking", "Blocking"),
        ],
        string="Severity",
        required=True,
        default="warning",
        help=(
            "Warning: creates an exception but does not block posting. "
            "Blocking: prevents posting until the exception is resolved or waived."
        ),
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Lower sequence rules are evaluated first.",
    )
    policy_reference = fields.Char(
        string="Policy Reference",
        help="BIR RR, NIRC section, or internal policy identifier this rule enforces.",
    )
    compliance_pack_id = fields.Many2one(
        "tax.compliance.pack",
        string="Compliance Pack",
        ondelete="set null",
        help="The compliance pack this rule belongs to, if any.",
    )

    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(name)",
            "Rule name must be unique.",
        ),
    ]
