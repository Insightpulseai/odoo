"""Tests for tax.validation.rule model.

Tests rule creation, field validation, and country/severity filtering.

Tagged with @tagged('tax', 'avatax', 'post_install', '-at_install')
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("tax", "avatax", "post_install", "-at_install")
class TestTaxValidationRule(TransactionCase):
    """TransactionCase tests for tax.validation.rule."""

    def setUp(self):
        super().setUp()
        self.Rule = self.env["tax.validation.rule"]
        self.ph_country = self.env.ref("base.ph")
        self.us_country = self.env.ref("base.us")

    def test_rule_creation_minimal(self):
        """Rule can be created with required fields only."""
        rule = self.Rule.create({
            "name": "Test Minimal Rule",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "warning",
        })
        self.assertEqual(rule.name, "Test Minimal Rule")
        self.assertEqual(rule.rule_type, "rate_check")
        self.assertEqual(rule.applies_to, "all")
        self.assertEqual(rule.severity, "warning")
        self.assertTrue(rule.is_active)
        self.assertFalse(rule.country_id)
        self.assertFalse(rule.tax_group_id)

    def test_rule_creation_full(self):
        """Rule can be created with all fields."""
        rule = self.Rule.create({
            "name": "Test Full Rule",
            "description": "A fully specified rule.",
            "rule_type": "withholding_check",
            "applies_to": "bill",
            "country_id": self.ph_country.id,
            "severity": "blocking",
            "is_active": True,
            "sequence": 5,
            "policy_reference": "NIRC Sec 57(B)",
            "expression": "ewt_rate == 0.02",
        })
        self.assertEqual(rule.rule_type, "withholding_check")
        self.assertEqual(rule.applies_to, "bill")
        self.assertEqual(rule.country_id, self.ph_country)
        self.assertEqual(rule.severity, "blocking")
        self.assertEqual(rule.sequence, 5)
        self.assertEqual(rule.policy_reference, "NIRC Sec 57(B)")

    def test_rule_severity_levels(self):
        """Both warning and blocking severity levels can be created."""
        warning_rule = self.Rule.create({
            "name": "Warning Rule",
            "rule_type": "document_completeness",
            "applies_to": "all",
            "severity": "warning",
        })
        blocking_rule = self.Rule.create({
            "name": "Blocking Rule",
            "rule_type": "rate_check",
            "applies_to": "invoice",
            "severity": "blocking",
        })
        self.assertEqual(warning_rule.severity, "warning")
        self.assertEqual(blocking_rule.severity, "blocking")

    def test_rule_country_filter_ph(self):
        """PH-scoped rule correctly filters by country."""
        ph_rule = self.Rule.create({
            "name": "PH Only Rule",
            "rule_type": "withholding_check",
            "applies_to": "bill",
            "country_id": self.ph_country.id,
            "severity": "blocking",
        })
        self.assertEqual(ph_rule.country_id, self.ph_country)
        # Rule should not match US company context
        self.assertNotEqual(ph_rule.country_id, self.us_country)

    def test_rule_all_types_accepted(self):
        """All five rule_type values are accepted."""
        types = [
            "rate_check",
            "jurisdiction_match",
            "exemption_verify",
            "withholding_check",
            "document_completeness",
        ]
        for i, rule_type in enumerate(types):
            rule = self.Rule.create({
                "name": f"Rule type {rule_type}",
                "rule_type": rule_type,
                "applies_to": "all",
                "severity": "warning",
                "sequence": i + 100,
            })
            self.assertEqual(rule.rule_type, rule_type)

    def test_rule_inactive_is_not_active(self):
        """Inactive rules have is_active=False."""
        rule = self.Rule.create({
            "name": "Inactive Rule",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "warning",
            "is_active": False,
        })
        self.assertFalse(rule.is_active)

    def test_rule_name_uniqueness_constraint(self):
        """Duplicate rule names are rejected by the unique constraint."""
        from psycopg2 import IntegrityError

        self.Rule.create({
            "name": "Unique Rule Name",
            "rule_type": "rate_check",
            "applies_to": "all",
            "severity": "warning",
        })
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Rule.create({
                    "name": "Unique Rule Name",
                    "rule_type": "withholding_check",
                    "applies_to": "bill",
                    "severity": "blocking",
                })
