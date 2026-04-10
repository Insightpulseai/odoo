# -*- coding: utf-8 -*-
"""
Tests for pulser.intent — tri-modal behavior taxonomy.

Validates: informational / navigational / transactional classification,
activation lifecycle, and domain assignment.
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("pulser", "joule", "post_install", "-at_install")
class TestPulserIntent(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Intent = self.env["pulser.intent"]

    # ---- Creation ----

    def test_intent_informational_creation(self):
        intent = self.Intent.create({
            "name": "Query Invoice Status",
            "intent_type": "informational",
            "domain": "accounting",
            "example_query": "What is the status of invoice INV-2026-0042?",
        })
        self.assertEqual(intent.intent_type, "informational")
        self.assertTrue(intent.is_active)

    def test_intent_navigational_creation(self):
        intent = self.Intent.create({
            "name": "Navigate to Expense List",
            "intent_type": "navigational",
            "domain": "expense",
        })
        self.assertEqual(intent.intent_type, "navigational")

    def test_intent_transactional_creation(self):
        intent = self.Intent.create({
            "name": "Submit Expense Report",
            "intent_type": "transactional",
            "domain": "expense",
        })
        self.assertEqual(intent.intent_type, "transactional")

    # ---- Types exist ----

    def test_intent_types_all_valid(self):
        """All three tri-modal types must be creatable."""
        types = ["informational", "navigational", "transactional"]
        for t in types:
            intent = self.Intent.create({
                "name": f"Test {t} intent",
                "intent_type": t,
            })
            self.assertEqual(intent.intent_type, t, f"Expected {t}, got {intent.intent_type}")

    # ---- Activation lifecycle ----

    def test_intent_activation_default_true(self):
        intent = self.Intent.create({
            "name": "Active by Default",
            "intent_type": "informational",
        })
        self.assertTrue(intent.is_active, "Intent should be active by default")

    def test_intent_deactivation(self):
        intent = self.Intent.create({
            "name": "Deactivatable Intent",
            "intent_type": "navigational",
        })
        intent.is_active = False
        self.assertFalse(intent.is_active)

    def test_intent_reactivation(self):
        intent = self.Intent.create({
            "name": "Reactivatable Intent",
            "intent_type": "transactional",
            "is_active": False,
        })
        intent.is_active = True
        self.assertTrue(intent.is_active)

    # ---- Domain field ----

    def test_intent_domain_assignment(self):
        intent = self.Intent.create({
            "name": "Project Budget Query",
            "intent_type": "informational",
            "domain": "project",
        })
        self.assertEqual(intent.domain, "project")

    def test_intent_domain_optional(self):
        """Domain is optional — intent without domain must still save."""
        intent = self.Intent.create({
            "name": "Generic Intent",
            "intent_type": "informational",
        })
        self.assertFalse(intent.domain)

    # ---- Uniqueness constraint ----

    def test_intent_name_unique(self):
        self.Intent.create({
            "name": "Unique Intent Name",
            "intent_type": "informational",
        })
        with self.assertRaises(Exception):
            self.Intent.create({
                "name": "Unique Intent Name",
                "intent_type": "navigational",
            })
