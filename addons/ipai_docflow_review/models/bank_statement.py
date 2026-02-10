from odoo import fields, models, api, _
from odoo.exceptions import UserError


class DocflowBankStatement(models.Model):
    _name = "docflow.bank.statement"
    _description = "DocFlow Bank Statement"
    _order = "date_from desc, id desc"

    name = fields.Char(required=True)
    document_id = fields.Many2one("docflow.document", required=True, ondelete="cascade")

    journal_id = fields.Many2one("account.journal", domain=[("type", "=", "bank")], required=True)
    currency_id = fields.Many2one("res.currency", required=True)

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    opening_balance = fields.Monetary(currency_field="currency_id")
    closing_balance = fields.Monetary(currency_field="currency_id")

    line_ids = fields.One2many(
        "docflow.bank.statement.line", "statement_id", string="Statement Lines"
    )


class DocflowBankStatementLine(models.Model):
    _name = "docflow.bank.statement.line"
    _description = "DocFlow Bank Statement Line"
    _order = "date asc, id asc"

    statement_id = fields.Many2one("docflow.bank.statement", required=True, ondelete="cascade")

    date = fields.Date(required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(related="statement_id.currency_id", store=True, readonly=True)

    direction = fields.Selection([("credit", "Credit"), ("debit", "Debit")], required=True)
    reference = fields.Char()
    memo = fields.Char()
    counterparty = fields.Char()

    # reconciliation linkage
    matched_model = fields.Selection(
        [
            ("account.payment", "Payment"),
            ("account.move", "Invoice"),
            ("account.bank.statement.line", "BSL"),
        ]
    )
    matched_id = fields.Integer()
    match_score = fields.Float(digits=(3, 2))
    match_reason = fields.Char()
    match_state = fields.Selection(
        [
            ("unmatched", "Unmatched"),
            ("suggested", "Suggested"),
            ("reconciled", "Reconciled"),
            ("rejected", "Rejected"),
        ],
        default="unmatched",
    )
