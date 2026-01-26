# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    """Extends bank statement line with reconciliation matching."""

    _inherit = "account.bank.statement.line"

    reconcile_model_ids = fields.Many2many(
        "account.reconcile.model",
        string="Matching Models",
        help="Reconciliation models that match this statement line",
    )
    match_confidence = fields.Float(
        string="Match Confidence",
        compute="_compute_match_confidence",
        store=True,
        help="Confidence score for auto-matching (0-100%)",
    )
    suggested_partner_id = fields.Many2one(
        "res.partner",
        string="Suggested Partner",
        compute="_compute_match_proposals",
        store=True,
    )
    suggested_account_id = fields.Many2one(
        "account.account",
        string="Suggested Account",
        compute="_compute_match_proposals",
        store=True,
    )

    @api.depends("payment_ref", "amount", "partner_id")
    def _compute_match_confidence(self):
        """Compute matching confidence based on available data."""
        for line in self:
            confidence = 0.0
            if line.partner_id:
                confidence += 40.0
            if line.payment_ref:
                confidence += 30.0
            if line.amount:
                confidence += 30.0
            line.match_confidence = min(confidence, 100.0)

    @api.depends("payment_ref", "amount")
    def _compute_match_proposals(self):
        """Generate matching proposals for statement lines."""
        for line in self:
            # Find partner by payment reference
            if line.payment_ref and not line.partner_id:
                partner = self.env["res.partner"].search(
                    ["|", ("name", "ilike", line.payment_ref),
                     ("ref", "=", line.payment_ref)],
                    limit=1,
                )
                line.suggested_partner_id = partner.id if partner else False
            else:
                line.suggested_partner_id = line.partner_id.id

            # Suggest account based on amount sign
            if line.amount > 0:
                # Income - suggest receivable
                line.suggested_account_id = self.env.company.account_journal_payment_debit_account_id.id
            else:
                # Expense - suggest payable
                line.suggested_account_id = self.env.company.account_journal_payment_credit_account_id.id

    def action_auto_reconcile(self):
        """Attempt automatic reconciliation based on proposals."""
        reconciled_count = 0
        for line in self:
            if line.match_confidence >= 80.0 and not line.is_reconciled:
                # Try to find matching move lines
                domain = [
                    ("reconciled", "=", False),
                    ("account_id.reconcile", "=", True),
                ]
                if line.partner_id:
                    domain.append(("partner_id", "=", line.partner_id.id))
                if line.amount:
                    domain.append(("amount_residual", "=", abs(line.amount)))

                move_lines = self.env["account.move.line"].search(domain, limit=1)
                if move_lines:
                    line.reconcile([{"id": move_lines.id}])
                    reconciled_count += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Auto Reconciliation Complete",
                "message": f"Reconciled {reconciled_count} statement lines",
                "type": "success",
            },
        }
