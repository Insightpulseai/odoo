"""Tests for tax.compliance.pack model.

Covers pack creation, PH BIR pack existence after install,
and rule linkage via compliance_pack_id.

Tagged with @tagged('tax', 'avatax', 'post_install', '-at_install')
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("tax", "avatax", "post_install", "-at_install")
class TestTaxCompliancePack(TransactionCase):
    """TransactionCase tests for tax.compliance.pack."""

    def setUp(self):
        super().setUp()
        self.Pack = self.env["tax.compliance.pack"]
        self.Rule = self.env["tax.validation.rule"]
        self.ph_country = self.env.ref("base.ph")
        self.us_country = self.env.ref("base.us")

    def test_ph_bir_pack_exists(self):
        """PH BIR compliance pack is pre-installed via data XML."""
        ph_packs = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("is_active", "=", True),
        ])
        self.assertGreater(len(ph_packs), 0, "PH BIR pack must exist after install.")
        ph_pack = ph_packs[0]
        self.assertEqual(ph_pack.country_id, self.ph_country)
        self.assertTrue(ph_pack.version)
        self.assertTrue(ph_pack.name)

    def test_ph_bir_pack_version(self):
        """PH BIR pack has version 1.0.0."""
        pack = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("version", "=", "1.0.0"),
        ], limit=1)
        self.assertTrue(pack, "PH BIR pack version 1.0.0 must exist.")

    def test_ph_bir_pack_has_rules(self):
        """PH BIR pack has at least 4 pre-loaded validation rules."""
        pack = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("version", "=", "1.0.0"),
        ], limit=1)
        self.assertTrue(pack)
        self.assertGreaterEqual(
            len(pack.rule_ids), 4,
            "PH BIR pack must have at least 4 rules (VAT, EWT, percentage tax, document completeness).",
        )

    def test_pack_rule_linkage(self):
        """Rules linked to a pack have correct compliance_pack_id."""
        pack = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("version", "=", "1.0.0"),
        ], limit=1)
        self.assertTrue(pack)
        for rule in pack.rule_ids:
            self.assertEqual(
                rule.compliance_pack_id,
                pack,
                f"Rule '{rule.name}' should be linked to the PH BIR pack.",
            )

    def test_pack_creation(self):
        """A new compliance pack can be created."""
        pack = self.Pack.create({
            "name": "US Federal Tax Pack",
            "country_id": self.us_country.id,
            "version": "1.0.0",
            "description": "US Federal tax compliance rules.",
            "is_active": True,
        })
        self.assertEqual(pack.name, "US Federal Tax Pack")
        self.assertEqual(pack.country_id, self.us_country)
        self.assertEqual(pack.version, "1.0.0")

    def test_pack_rule_count_computed(self):
        """rule_count is computed from rule_ids."""
        pack = self.Pack.create({
            "name": "Test Pack For Rule Count",
            "country_id": self.us_country.id,
            "version": "9.9.9",
            "is_active": True,
        })
        self.assertEqual(pack.rule_count, 0)

        # Create a rule linked to this pack
        self.Rule.create({
            "name": "Pack Rule Count Test Rule",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "warning",
            "compliance_pack_id": pack.id,
        })
        pack.invalidate_recordset(["rule_count"])
        self.assertEqual(pack.rule_count, 1)

    def test_pack_unique_country_version_constraint(self):
        """Two packs cannot share the same country and version."""
        from psycopg2 import IntegrityError

        self.Pack.create({
            "name": "Duplicate Version Pack A",
            "country_id": self.us_country.id,
            "version": "2.0.0",
            "is_active": True,
        })
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Pack.create({
                    "name": "Duplicate Version Pack B",
                    "country_id": self.us_country.id,
                    "version": "2.0.0",
                    "is_active": True,
                })

    def test_ph_bir_pack_rules_contain_withholding(self):
        """PH BIR pack contains at least one withholding_check rule."""
        pack = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("version", "=", "1.0.0"),
        ], limit=1)
        self.assertTrue(pack)
        withholding_rules = pack.rule_ids.filtered(
            lambda r: r.rule_type == "withholding_check"
        )
        self.assertGreater(
            len(withholding_rules), 0,
            "PH BIR pack must contain at least one withholding_check rule.",
        )

    def test_ph_bir_pack_rules_contain_document_completeness(self):
        """PH BIR pack contains at least one document_completeness rule."""
        pack = self.Pack.search([
            ("country_id", "=", self.ph_country.id),
            ("version", "=", "1.0.0"),
        ], limit=1)
        self.assertTrue(pack)
        doc_rules = pack.rule_ids.filtered(
            lambda r: r.rule_type == "document_completeness"
        )
        self.assertGreater(
            len(doc_rules), 0,
            "PH BIR pack must contain at least one document_completeness rule.",
        )
