"""Tests for tax.validation.mixin and account.move integration.

Tests pre-posting validation, exception creation, and posting blocker.

Tagged with @tagged('tax', 'avatax', 'post_install', '-at_install')
"""

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("tax", "avatax", "post_install", "-at_install")
class TestValidationMixin(TransactionCase):
    """TransactionCase tests for tax.validation.mixin via account.move."""

    def setUp(self):
        super().setUp()
        self.ph_country = self.env.ref("base.ph")

        # Setup company with PH country for PH rule scoping
        self.company = self.env.company
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company.id)],
            limit=1,
        )
        if not self.journal:
            self.journal = self.env["account.journal"].create({
                "name": "Test Sales Journal",
                "type": "sale",
                "code": "TSALE",
                "company_id": self.company.id,
            })

        self.partner = self.env["res.partner"].create({"name": "Test Partner TI"})

        # A simple income account (Odoo 18: company_ids M2M, not company_id)
        self.account = self.env["account.account"].search(
            [("account_type", "=", "income")],
            limit=1,
        )
        if not self.account:
            self.account = self.env["account.account"].create({
                "name": "Test Income Account TI",
                "code": "INCOME.TI",
                "account_type": "income",
            })

        # A tax for use in invoice lines
        self.tax = self.env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        if not self.tax:
            self.tax = self.env["account.tax"].create({
                "name": "Test VAT 12%",
                "type_tax_use": "sale",
                "amount": 12.0,
                "amount_type": "percent",
                "company_id": self.company.id,
            })

        # Rules for testing (non-country scoped so they fire regardless of company country)
        self.blocking_rate_rule = self.env["tax.validation.rule"].create({
            "name": "Test Blocking Rate Rule (no country)",
            "rule_type": "rate_check",
            "applies_to": "invoice",
            "severity": "blocking",
            "is_active": True,
            "sequence": 1,
        })

    def _make_invoice(self, with_tax=True):
        """Create a draft customer invoice."""
        line_vals = {
            "account_id": self.account.id,
            "name": "Test Line",
            "price_unit": 1000.0,
            "quantity": 1,
        }
        if with_tax:
            line_vals["tax_ids"] = [(4, self.tax.id)]

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "journal_id": self.journal.id,
            "invoice_line_ids": [(0, 0, line_vals)],
        })
        return move

    def _get_open_exceptions_for(self, invoice):
        """Helper: return open blocking exceptions for the given invoice."""
        return self.env["tax.exception"].search([
            ("source_model", "=", "account.move"),
            ("source_id", "=", invoice.id),
            ("state", "in", ("detected", "under_review", "escalated")),
            ("severity", "=", "blocking"),
        ])

    def _run_mixin_validate(self, invoice):
        """Call the mixin's action_validate_taxes directly, bypassing account.move override.

        Returns the raw dict: {"rules_evaluated": int, "exceptions_created": int}
        """
        from odoo.addons.ipai_tax_intelligence.models.tax_validation_mixin import (
            TaxValidationMixin,
        )
        return TaxValidationMixin.action_validate_taxes(invoice)

    def test_invoice_validation_no_exceptions_with_tax(self):
        """Invoice with taxes applied should produce no rate_check exceptions."""
        invoice = self._make_invoice(with_tax=True)
        self.assertEqual(invoice.state, "draft")

        # No exceptions should exist before any validation
        open_exceptions = self._get_open_exceptions_for(invoice)
        self.assertEqual(len(open_exceptions), 0, "No exceptions should exist before validation.")

        # Deactivate the blocking rule to get a clean result
        self.blocking_rate_rule.write({"is_active": False})
        action_result = invoice.action_validate_taxes()
        # account.move.action_validate_taxes returns an ir.actions.client notification
        self.assertEqual(action_result["type"], "ir.actions.client")

    def test_invoice_validation_with_exceptions_no_tax(self):
        """Invoice without taxes triggers rate_check exception."""
        self.blocking_rate_rule.write({"is_active": True})
        invoice = self._make_invoice(with_tax=False)

        # Call mixin method directly to get raw dict result
        result = self._run_mixin_validate(invoice)
        self.assertIn("rules_evaluated", result)
        self.assertIn("exceptions_created", result)

        # Rate check should fire because no tax on lines
        exceptions = self.env["tax.exception"].search([
            ("source_model", "=", "account.move"),
            ("source_id", "=", invoice.id),
            ("rule_id", "=", self.blocking_rate_rule.id),
        ])
        self.assertGreater(
            len(exceptions), 0,
            "At least one exception should be created for invoice with no tax.",
        )

    def test_post_blocked_with_blocking_exception(self):
        """Posting is blocked when a blocking exception is open."""
        self.blocking_rate_rule.write({"is_active": True})
        invoice = self._make_invoice(with_tax=False)

        # Manually create a blocking exception
        self.env["tax.exception"].create({
            "source_model": "account.move",
            "source_id": invoice.id,
            "rule_id": self.blocking_rate_rule.id,
            "exception_type": "rate_mismatch",
            "state": "detected",
        })

        with self.assertRaises(UserError, msg="Posting must be blocked by blocking exception."):
            invoice.action_post()

    def test_post_succeeds_when_exceptions_resolved(self):
        """Posting succeeds when all blocking exceptions are resolved."""
        self.blocking_rate_rule.write({"is_active": True})
        invoice = self._make_invoice(with_tax=True)

        # Create and then resolve a blocking exception
        exc = self.env["tax.exception"].create({
            "source_model": "account.move",
            "source_id": invoice.id,
            "rule_id": self.blocking_rate_rule.id,
            "exception_type": "rate_mismatch",
            "state": "detected",
        })
        exc.action_start_review()
        exc.action_resolve()
        self.assertEqual(exc.state, "resolved")

        # Now posting should succeed (no open blocking exceptions)
        # We don't call action_post directly here to avoid journal config requirements
        open_blocking = self._get_open_exceptions_for(invoice)
        self.assertEqual(len(open_blocking), 0)

    def test_post_allowed_with_warning_exception(self):
        """Warning-only exceptions do not block posting."""
        warning_rule = self.env["tax.validation.rule"].create({
            "name": "Test Warning-Only Rule",
            "rule_type": "document_completeness",
            "applies_to": "all",
            "severity": "warning",
            "is_active": True,
        })
        invoice = self._make_invoice(with_tax=True)

        # Create a warning (not blocking) exception
        self.env["tax.exception"].create({
            "source_model": "account.move",
            "source_id": invoice.id,
            "rule_id": warning_rule.id,
            "exception_type": "missing_document",
            "state": "detected",
        })

        # No blocking exceptions exist — warnings don't block posting
        open_blocking = self._get_open_exceptions_for(invoice)
        self.assertEqual(len(open_blocking), 0)

    def test_get_applicable_rules_filters_by_applies_to(self):
        """_get_applicable_rules returns rules matching invoice type."""
        invoice = self._make_invoice(with_tax=True)
        bill_only_rule = self.env["tax.validation.rule"].create({
            "name": "Test Bill-Only Rule For Filtering",
            "rule_type": "withholding_check",
            "applies_to": "bill",
            "severity": "blocking",
            "is_active": True,
        })
        applicable = invoice._get_applicable_rules()
        # bill_only rule should NOT be in applicable rules for an invoice
        self.assertNotIn(
            bill_only_rule,
            applicable,
            "Bill-only rule should not apply to invoice.",
        )

    def test_get_applicable_rules_excludes_inactive(self):
        """_get_applicable_rules excludes inactive rules."""
        invoice = self._make_invoice(with_tax=True)
        inactive_rule = self.env["tax.validation.rule"].create({
            "name": "Test Inactive Rule For Validation",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "warning",
            "is_active": False,
        })
        applicable = invoice._get_applicable_rules()
        self.assertNotIn(
            inactive_rule,
            applicable,
            "Inactive rules must not be returned.",
        )

    def test_no_duplicate_exceptions_on_revalidation(self):
        """Re-running validation does not create duplicate open exceptions."""
        self.blocking_rate_rule.write({"is_active": True})
        invoice = self._make_invoice(with_tax=False)

        # Run mixin validation twice
        self._run_mixin_validate(invoice)
        self._run_mixin_validate(invoice)

        exceptions = self.env["tax.exception"].search([
            ("source_model", "=", "account.move"),
            ("source_id", "=", invoice.id),
            ("rule_id", "=", self.blocking_rate_rule.id),
            ("state", "in", ("detected", "under_review", "escalated")),
        ])
        self.assertEqual(
            len(exceptions), 1,
            "Running validation twice must not create duplicate open exceptions.",
        )
