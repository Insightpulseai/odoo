# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountReconcileModel(models.Model):
    """Reconciliation matching model for automated bank reconciliation."""

    _name = "account.reconcile.model"
    _description = "Bank Reconciliation Matching Model"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    rule_type = fields.Selection(
        [
            ("writeoff_button", "Button to generate counterpart entry"),
            ("writeoff_suggestion", "Rule to suggest counterpart entry"),
            ("invoice_matching", "Rule to match invoices/bills"),
        ],
        default="writeoff_suggestion",
        required=True,
    )
    match_partner = fields.Boolean(
        string="Match Partner",
        default=True,
        help="Match only lines with same partner",
    )
    match_amount = fields.Selection(
        [
            ("lower", "Amount is lower than"),
            ("lower_or_equal", "Amount is lower or equal"),
            ("equal", "Amount is equal to"),
            ("greater_or_equal", "Amount is greater or equal"),
            ("greater", "Amount is greater than"),
            ("between", "Amount is between"),
        ],
        string="Amount Matching",
    )
    match_amount_min = fields.Float(string="Minimum Amount")
    match_amount_max = fields.Float(string="Maximum Amount")
    match_label = fields.Selection(
        [
            ("contains", "Contains"),
            ("not_contains", "Not Contains"),
            ("match_regex", "Matches Regex"),
        ],
        string="Label Matching",
    )
    match_label_param = fields.Char(string="Label Parameter")
    account_id = fields.Many2one(
        "account.account",
        string="Counterpart Account",
        help="Account to use for the counterpart entry",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        help="Journal to use for the counterpart entry",
    )
    label = fields.Char(
        string="Counterpart Label",
        help="Label for the counterpart entry",
    )

    def _get_matching_lines(self, statement_line):
        """Get move lines matching this reconciliation model."""
        self.ensure_one()
        domain = [
            ("reconciled", "=", False),
            ("account_id.reconcile", "=", True),
            ("company_id", "=", statement_line.company_id.id),
        ]

        if self.match_partner and statement_line.partner_id:
            domain.append(("partner_id", "=", statement_line.partner_id.id))

        if self.match_amount:
            amount = abs(statement_line.amount)
            if self.match_amount == "lower":
                domain.append(("amount_residual", "<", amount))
            elif self.match_amount == "lower_or_equal":
                domain.append(("amount_residual", "<=", amount))
            elif self.match_amount == "equal":
                domain.append(("amount_residual", "=", amount))
            elif self.match_amount == "greater_or_equal":
                domain.append(("amount_residual", ">=", amount))
            elif self.match_amount == "greater":
                domain.append(("amount_residual", ">", amount))
            elif self.match_amount == "between":
                domain.append(("amount_residual", ">=", self.match_amount_min))
                domain.append(("amount_residual", "<=", self.match_amount_max))

        return self.env["account.move.line"].search(domain)
