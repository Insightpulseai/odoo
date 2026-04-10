# -*- coding: utf-8 -*-
"""
test_boundary_doc.py — Tests for expense.boundary.doc model.

Verifies:
  - All 5 layers have at least one documented capability
  - CE native capabilities are declared/proven
  - OCA capabilities are documented
  - Gap entries exist for known gaps
  - Status transition from declared to proven is permitted
"""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("expense", "liquidation", "post_install", "-at_install")
class TestBoundaryDoc(TransactionCase):
    """Test expense.boundary.doc model coverage and data integrity."""

    def setUp(self):
        super().setUp()
        self.BoundaryDoc = self.env["expense.boundary.doc"]

    # ── Layer coverage ─────────────────────────────────────────────────────

    def test_boundary_layers_exist(self):
        """All 5 defined layers must have at least one boundary doc record."""
        expected_layers = {"ce_native", "oca_direct", "oca_adjacent", "custom_delta", "bridge"}
        for layer in expected_layers:
            count = self.BoundaryDoc.search_count([("layer", "=", layer)])
            self.assertGreater(
                count,
                0,
                msg=f"Layer '{layer}' has no boundary documentation records.",
            )

    # ── CE native capabilities ─────────────────────────────────────────────

    def test_ce_native_capabilities_documented(self):
        """CE native layer must document core expense capabilities."""
        ce_records = self.BoundaryDoc.search([("layer", "=", "ce_native")])
        capabilities = ce_records.mapped("capability")
        # Submission workflow must be documented
        self.assertTrue(
            any("submission" in cap.lower() for cap in capabilities),
            "CE native layer missing: expense report submission capability.",
        )
        # Posting must be documented
        self.assertTrue(
            any("posting" in cap.lower() for cap in capabilities),
            "CE native layer missing: journal entry posting capability.",
        )

    def test_ce_native_status_not_gap(self):
        """CE native capabilities must not be marked as gap (they exist in CE)."""
        gap_records = self.BoundaryDoc.search(
            [("layer", "=", "ce_native"), ("status", "=", "gap")]
        )
        self.assertEqual(
            len(gap_records),
            0,
            msg=f"CE native layer has 'gap' records (should not): {gap_records.mapped('capability')}",
        )

    # ── OCA direct capabilities ────────────────────────────────────────────

    def test_oca_capabilities_documented(self):
        """OCA direct layer must document key OCA/hr-expense modules."""
        oca_records = self.BoundaryDoc.search([("layer", "=", "oca_direct")])
        modules = oca_records.mapped("module_name")
        self.assertTrue(
            any("advance_clearing" in m for m in modules),
            "OCA direct layer missing: hr_expense_advance_clearing documentation.",
        )
        self.assertTrue(
            any("tier_validation" in m for m in modules),
            "OCA direct layer missing: hr_expense_tier_validation documentation.",
        )

    # ── OCA adjacent wiring ────────────────────────────────────────────────

    def test_oca_adjacent_p1_modules_documented(self):
        """P1 OCA adjacent modules (dms, auditlog, queue_job) must be documented."""
        adjacent = self.BoundaryDoc.search([("layer", "=", "oca_adjacent")])
        modules = " ".join(adjacent.mapped("module_name"))
        self.assertIn("dms", modules, "OCA adjacent: dms wiring not documented.")
        self.assertIn("auditlog", modules, "OCA adjacent: auditlog wiring not documented.")
        self.assertIn("queue_job", modules, "OCA adjacent: queue_job wiring not documented.")

    # ── Custom delta scope ─────────────────────────────────────────────────

    def test_custom_delta_ph_capabilities_documented(self):
        """Custom delta layer must document PH-specific capabilities."""
        delta = self.BoundaryDoc.search([("layer", "=", "custom_delta")])
        capabilities = " ".join(delta.mapped("capability")).lower()
        self.assertIn("cash advance", capabilities, "Custom delta missing: cash advance capability.")
        self.assertIn("liquidation", capabilities, "Custom delta missing: liquidation capability.")
        self.assertIn("bir", capabilities, "Custom delta missing: BIR compliance capability.")

    # ── Gap documentation ──────────────────────────────────────────────────

    def test_gap_documentation(self):
        """Known gaps must be documented: card feed, mileage, mobile capture.

        Note: OCR (Azure Document Intelligence) is classified as 'candidate' in the
        bridge layer (boundary_bridge_ocr), not 'gap', because a viable solution path
        exists. It is verified separately via test_ocr_candidate_documented.
        """
        gap_records = self.BoundaryDoc.search([("status", "=", "gap")])
        self.assertGreater(
            len(gap_records), 0, "No gap records found — known gaps must be documented."
        )
        all_text = " ".join(
            gap_records.mapped("notes") + gap_records.mapped("capability")
        ).lower()
        self.assertIn("card", all_text, "Gap records missing: corporate card feed gap not documented.")
        self.assertIn("mileage", all_text, "Gap records missing: mileage/per-diem gap not documented.")

    def test_ocr_candidate_documented(self):
        """OCR bridge must be documented as a candidate (Azure DI solution path exists)."""
        ocr_records = self.BoundaryDoc.search(
            [("layer", "=", "bridge"), ("status", "=", "candidate")]
        )
        notes_concat = " ".join(ocr_records.mapped("notes")).lower()
        self.assertIn(
            "ocr",
            notes_concat,
            "Bridge candidate records missing: OCR/Azure Document Intelligence not documented.",
        )

    def test_bridge_layer_has_gaps(self):
        """Bridge layer must have at least one gap record (known unresolved items)."""
        bridge_gaps = self.BoundaryDoc.search(
            [("layer", "=", "bridge"), ("status", "=", "gap")]
        )
        self.assertGreater(
            len(bridge_gaps),
            0,
            "Bridge layer has no gap records — expected at least card feed and mileage/per-diem.",
        )

    # ── Status transitions ─────────────────────────────────────────────────

    def test_status_transitions(self):
        """Status can be changed from declared to proven (verification workflow)."""
        record = self.BoundaryDoc.create(
            {
                "layer": "ce_native",
                "module_name": "hr_expense",
                "capability": "Test capability for status transition",
                "status": "declared",
            }
        )
        self.assertEqual(record.status, "declared")

        record.write({"status": "proven", "verified_date": "2026-04-10"})
        self.assertEqual(record.status, "proven")
        self.assertEqual(str(record.verified_date), "2026-04-10")

    def test_all_valid_status_values(self):
        """All four status values must be creatable."""
        for status in ("proven", "declared", "candidate", "gap"):
            record = self.BoundaryDoc.create(
                {
                    "layer": "bridge",
                    "module_name": "test_module",
                    "capability": f"Test capability [{status}]",
                    "status": status,
                }
            )
            self.assertEqual(record.status, status)
            record.unlink()

    # ── Company field ──────────────────────────────────────────────────────

    def test_company_id_defaults(self):
        """company_id must default to current company."""
        record = self.BoundaryDoc.create(
            {
                "layer": "ce_native",
                "module_name": "hr_expense",
                "capability": "Company default test",
                "status": "declared",
            }
        )
        self.assertEqual(record.company_id, self.env.company)
        record.unlink()
