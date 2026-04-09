"""Tests for BIR export batch — Phase 4 compliance datasets."""

import json

from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestBIRExport(TransactionCase):
    """Test BIR export batch generation and state management."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "BIR Export Vendor",
            "vat": "123-456-789-000",
        })
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        cls.move = cls.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": cls.partner.id,
            "journal_id": cls.journal.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Consulting service",
                "quantity": 1,
                "price_unit": 200000.0,
            })],
        })
        cls.review = cls.env["ipai.tax.review"].create({
            "move_id": cls.move.id,
            "state": "validated",
            "expected_subtotal": 200000.0,
            "expected_vat": 24000.0,
            "expected_gross": 224000.0,
            "expected_withholding": 4000.0,
            "expected_payable": 220000.0,
            "printed_total_due": 220000.0,
            "delta": 0.0,
            "extraction_confidence": 0.98,
        })

    def test_create_batch_default_state(self):
        """New batch starts in draft."""
        batch = self.env["ipai.bir.export.batch"].create({
            "date_from": "2026-01-01",
            "date_to": "2026-03-31",
            "export_type": "purchases",
            "review_ids": [(6, 0, [self.review.id])],
        })
        self.assertEqual(batch.state, "draft")
        self.assertEqual(batch.review_count, 1)

    def test_generate_export_data(self):
        """Generate produces valid JSON with correct record count."""
        batch = self.env["ipai.bir.export.batch"].create({
            "date_from": "2026-01-01",
            "date_to": "2026-03-31",
            "export_type": "purchases",
            "review_ids": [(6, 0, [self.review.id])],
        })
        batch.action_generate()
        self.assertEqual(batch.state, "generated")
        self.assertTrue(batch.export_data)

        data = json.loads(batch.export_data)
        self.assertEqual(data["record_count"], 1)
        self.assertEqual(data["export_type"], "purchases")
        self.assertAlmostEqual(data["records"][0]["expected_payable"], 220000.0)

    def test_mark_exported(self):
        """Mark as exported transitions state."""
        batch = self.env["ipai.bir.export.batch"].create({
            "date_from": "2026-01-01",
            "date_to": "2026-03-31",
            "export_type": "withholding",
            "review_ids": [(6, 0, [self.review.id])],
        })
        batch.action_generate()
        batch.action_mark_exported()
        self.assertEqual(batch.state, "exported")

    def test_reset_to_draft(self):
        """Reset clears export data and returns to draft."""
        batch = self.env["ipai.bir.export.batch"].create({
            "date_from": "2026-01-01",
            "date_to": "2026-03-31",
            "export_type": "sales",
            "review_ids": [(6, 0, [self.review.id])],
        })
        batch.action_generate()
        batch.action_reset_to_draft()
        self.assertEqual(batch.state, "draft")
        self.assertFalse(batch.export_data)
