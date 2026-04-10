"""IPAI Tax Intelligence — account.move extension.

Adds tax exception tracking, pre-posting validation hook, and smart button
to the Odoo account.move (invoice/bill) form.

Constitution Principle 1: Odoo owns invoices, tax lines, and posting truth.
Constitution Principle 6: Draft-first — blocking exceptions prevent posting.
"""

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Tax intelligence extension for account.move."""

    _name = "account.move"
    _inherit = ["account.move", "tax.validation.mixin"]

    tax_exception_ids = fields.One2many(
        "tax.exception",
        compute="_compute_tax_exception_ids",
        string="Tax Exceptions",
    )
    tax_exception_count = fields.Integer(
        string="Tax Exception Count",
        compute="_compute_tax_exception_count",
    )
    tax_validation_state = fields.Selection(
        [
            ("not_validated", "Not Validated"),
            ("clean", "Clean"),
            ("has_warnings", "Has Warnings"),
            ("has_blocking", "Blocking Exceptions"),
        ],
        string="Tax Validation State",
        compute="_compute_tax_validation_state",
        store=False,
    )

    def _compute_tax_exception_ids(self):
        TaxException = self.env["tax.exception"]
        for move in self:
            if move._origin.id:
                move.tax_exception_ids = TaxException.search([
                    ("source_model", "=", "account.move"),
                    ("source_id", "=", move._origin.id),
                ])
            else:
                move.tax_exception_ids = TaxException

    def _compute_tax_exception_count(self):
        TaxException = self.env["tax.exception"]
        for move in self:
            if move._origin.id:
                move.tax_exception_count = TaxException.search_count([
                    ("source_model", "=", "account.move"),
                    ("source_id", "=", move._origin.id),
                ])
            else:
                move.tax_exception_count = 0

    def _compute_tax_validation_state(self):
        for move in self:
            exceptions = move.tax_exception_ids.filtered(
                lambda e: e.state in ("detected", "under_review", "escalated")
            )
            if not exceptions:
                all_exceptions = move.tax_exception_ids
                if all_exceptions:
                    move.tax_validation_state = "clean"
                else:
                    move.tax_validation_state = "not_validated"
            elif any(e.severity == "blocking" for e in exceptions):
                move.tax_validation_state = "has_blocking"
            else:
                move.tax_validation_state = "has_warnings"

    def action_post(self):
        """Block posting when blocking tax exceptions are open."""
        for move in self:
            blocking_exceptions = self.env["tax.exception"].search([
                ("source_model", "=", "account.move"),
                ("source_id", "=", move.id),
                ("state", "in", ("detected", "under_review", "escalated")),
                ("severity", "=", "blocking"),
            ])
            if blocking_exceptions:
                names = ", ".join(blocking_exceptions.mapped("name"))
                raise UserError(
                    "This document has unresolved blocking tax exceptions and cannot be posted.\n\n"
                    f"Open exceptions: {names}\n\n"
                    "Resolve or waive all blocking exceptions before posting."
                )
        return super().action_post()

    def action_validate_taxes(self):
        """Trigger pre-posting tax validation for this invoice/bill."""
        self.ensure_one()
        result = super().action_validate_taxes()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Tax Validation Complete",
                "message": (
                    f"Rules evaluated: {result['rules_evaluated']}. "
                    f"New exceptions: {result['exceptions_created']}."
                ),
                "type": "success" if result["exceptions_created"] == 0 else "warning",
                "sticky": False,
            },
        }

    def action_view_tax_exceptions(self):
        """Open tax exceptions list for this document."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tax Exceptions",
            "res_model": "tax.exception",
            "domain": [
                ("source_model", "=", "account.move"),
                ("source_id", "=", self.id),
            ],
            "view_mode": "list,form",
            "context": {
                "default_source_model": "account.move",
                "default_source_id": self.id,
            },
        }
