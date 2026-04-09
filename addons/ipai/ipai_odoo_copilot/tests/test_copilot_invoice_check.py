# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""Odoo-native tests for copilot invoice validation integration.

Tests the ipai.copilot.invoice.check model and the deterministic
validator integration with the Odoo ORM layer.

The ph_invoice_math pure-logic tests live in test_ph_invoice_math.py
(standalone, no Odoo). These tests verify the Odoo model layer on top.
"""

import json

from odoo.tests import TransactionCase, tagged


class TestCopilotInvoiceCheck(TransactionCase):
    """Tests for ipai.copilot.invoice.check model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.InvoiceCheck = cls.env["ipai.copilot.invoice.check"]

    def test_create_validated_check(self):
        """Create a validated invoice check record."""
        check = self.InvoiceCheck.create({
            "status": "validated",
            "expected_payable": 95408.16,
            "printed_total_due": 95408.16,
            "delta": 0.0,
            "findings_json": "[]",
            "summary": "All invoice math checks passed.",
        })
        self.assertEqual(check.status, "validated")
        self.assertAlmostEqual(check.delta, 0.0, places=2)

    def test_create_needs_review_check(self):
        """Create a needs_review invoice check with findings."""
        findings = [
            {
                "code": "PRINTED_TOTAL_DUE_MISMATCH",
                "expected": "95408.16",
                "actual": "85000.00",
                "delta": "10408.16",
                "severity": "error",
            },
        ]
        check = self.InvoiceCheck.create({
            "status": "needs_review",
            "expected_payable": 95408.16,
            "printed_total_due": 85000.00,
            "delta": 10408.16,
            "findings_json": json.dumps(findings),
            "summary": "Invoice math validation found issues:\n"
                       "- PRINTED_TOTAL_DUE_MISMATCH: expected 95408.16, "
                       "got 85000.00 (delta: 10408.16)",
        })
        self.assertEqual(check.status, "needs_review")
        self.assertAlmostEqual(check.delta, 10408.16, places=2)

        parsed = json.loads(check.findings_json)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["code"], "PRINTED_TOTAL_DUE_MISMATCH")

    def test_default_status_is_needs_review(self):
        check = self.InvoiceCheck.create({
            "expected_payable": 100.0,
            "printed_total_due": 90.0,
        })
        self.assertEqual(check.status, "needs_review")

    def test_currency_default_php(self):
        """Default currency should be PHP if available."""
        php = self.env.ref("base.PHP", raise_if_not_found=False)
        check = self.InvoiceCheck.create({
            "status": "validated",
            "expected_payable": 100.0,
            "printed_total_due": 100.0,
        })
        if php:
            self.assertEqual(check.currency_id.id, php.id)

    def test_link_to_attachment_ref(self):
        """Invoice check can link to an attachment ref."""
        conv = self.env["ipai.copilot.conversation"].create({
            "name": "Invoice Test",
        })
        import base64
        att = self.env["ir.attachment"].create({
            "name": "invoice.pdf",
            "datas": base64.b64encode(b"fake pdf").decode(),
            "mimetype": "application/pdf",
            "type": "binary",
        })
        ref = self.env["ipai.copilot.attachment.ref"].create({
            "attachment_id": att.id,
            "conversation_id": conv.id,
            "filename": "invoice.pdf",
            "mime_type": "application/pdf",
            "origin": "upload",
        })
        check = self.InvoiceCheck.create({
            "attachment_ref_id": ref.id,
            "status": "needs_review",
            "expected_payable": 95408.16,
            "printed_total_due": 85000.00,
            "delta": 10408.16,
            "findings_json": "[]",
        })
        self.assertEqual(check.attachment_ref_id.id, ref.id)

    def test_cascade_delete_with_ref(self):
        """Deleting attachment ref cascades to invoice check."""
        conv = self.env["ipai.copilot.conversation"].create({
            "name": "Cascade Test",
        })
        import base64
        att = self.env["ir.attachment"].create({
            "name": "inv.pdf",
            "datas": base64.b64encode(b"test").decode(),
            "mimetype": "application/pdf",
            "type": "binary",
        })
        ref = self.env["ipai.copilot.attachment.ref"].create({
            "attachment_id": att.id,
            "conversation_id": conv.id,
            "filename": "inv.pdf",
            "mime_type": "application/pdf",
            "origin": "upload",
        })
        check = self.InvoiceCheck.create({
            "attachment_ref_id": ref.id,
            "status": "validated",
            "expected_payable": 100.0,
            "printed_total_due": 100.0,
        })
        check_id = check.id
        ref.unlink()
        self.assertFalse(self.InvoiceCheck.browse(check_id).exists())


class TestValidatorIntegration(TransactionCase):
    """Test that the pure-Python validator can be called from Odoo context."""

    def test_import_validator(self):
        """ph_invoice_math.validate is importable from Odoo addon path."""
        from odoo.addons.ipai_odoo_copilot.validators.ph_invoice_math import validate
        self.assertTrue(callable(validate))

    def test_validate_correct_invoice(self):
        """Correct invoice passes validation when called from Odoo."""
        from odoo.addons.ipai_odoo_copilot.validators.ph_invoice_math import validate

        doc = {
            "lines": [{"description": "Svc", "qty": 1,
                        "unit_cost": 100000.0, "amount": 100000.0}],
            "net_of_vat": 100000.0,
            "vat_rate": 0.12,
            "vat_amount": 12000.0,
            "gross_total": 112000.0,
            "withholding_rate": 0.02,
            "withholding_amount": 2000.0,
            "printed_total_due": 110000.0,
        }
        result = validate(doc)
        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["findings"], [])

    def test_validate_dataverse_mismatch(self):
        """Dataverse/TBWA invoice mismatch detected from Odoo."""
        from odoo.addons.ipai_odoo_copilot.validators.ph_invoice_math import validate

        doc = {
            "lines": [{"description": "Prof Svcs — Mar 2026", "qty": 1,
                        "unit_cost": 86734.69, "amount": 86734.69}],
            "net_of_vat": 86734.69,
            "vat_rate": 0.12,
            "vat_amount": 10408.16,
            "gross_total": 97142.85,
            "withholding_rate": 0.02,
            "withholding_amount": 1734.69,
            "printed_total_due": 85000.00,
        }
        result = validate(doc)
        self.assertEqual(result["status"], "needs_review")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("PRINTED_TOTAL_DUE_MISMATCH", codes)

    def test_store_validation_result(self):
        """Run validator and persist result to Odoo model."""
        from odoo.addons.ipai_odoo_copilot.validators.ph_invoice_math import validate

        doc = {
            "net_of_vat": 86734.69,
            "vat_rate": 0.12,
            "vat_amount": 10408.16,
            "gross_total": 97142.85,
            "withholding_rate": 0.02,
            "withholding_amount": 1734.69,
            "printed_total_due": 85000.00,
        }
        result = validate(doc)

        check = self.env["ipai.copilot.invoice.check"].create({
            "status": result["status"],
            "expected_payable": float(result["expected_payable"]),
            "printed_total_due": float(result["printed_total_due"]),
            "delta": float(result["expected_payable"]) - float(result["printed_total_due"]),
            "findings_json": json.dumps(result["findings"]),
            "summary": "Test validation",
        })
        self.assertEqual(check.status, "needs_review")
        self.assertAlmostEqual(check.expected_payable, 95408.16, places=2)
        self.assertAlmostEqual(check.delta, 10408.16, places=2)
