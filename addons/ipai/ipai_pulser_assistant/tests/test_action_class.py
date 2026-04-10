# -*- coding: utf-8 -*-
"""
Tests for pulser.action.class — safe action gate classification.

Validates: advisory never requires approval, approval_gated always does,
auto_routable constraints, max_auto_route_level bounds.
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("pulser", "joule", "post_install", "-at_install")
class TestPulserActionClass(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ActionClass = self.env["pulser.action.class"]

    def _make(self, name, class_type, max_level=0):
        return self.ActionClass.create({
            "name": name,
            "class_type": class_type,
            "max_auto_route_level": max_level,
        })

    # ---- Advisory ----

    def test_advisory_no_approval(self):
        ac = self._make("Advisory Read", "advisory")
        self.assertEqual(ac.class_type, "advisory")
        self.assertFalse(ac.requires_approval, "Advisory class must not require approval")

    def test_advisory_max_route_level_zero(self):
        """Advisory class must have max_auto_route_level=0."""
        ac = self._make("Advisory Only", "advisory", max_level=0)
        self.assertEqual(ac.max_auto_route_level, 0)

    def test_advisory_nonzero_level_raises(self):
        with self.assertRaises(ValidationError):
            self._make("Bad Advisory", "advisory", max_level=1)

    # ---- Approval-Gated ----

    def test_approval_gated_requires_approval(self):
        ac = self._make("Expense Submit Gate", "approval_gated")
        self.assertTrue(ac.requires_approval, "Approval-gated class must require approval")

    def test_approval_gated_computed_field(self):
        ac = self._make("Approve PO", "approval_gated")
        self.assertEqual(ac.requires_approval, True)

    def test_approval_gated_nonzero_level_raises(self):
        with self.assertRaises(ValidationError):
            self._make("Bad Gate", "approval_gated", max_level=1)

    # ---- Auto-Routable ----

    def test_auto_routable_no_forced_approval(self):
        ac = self._make("Mark Task Done", "auto_routable", max_level=1)
        self.assertFalse(ac.requires_approval, "Auto-routable must not force approval")

    def test_auto_routable_level_1(self):
        ac = self._make("Low Risk Auto", "auto_routable", max_level=1)
        self.assertEqual(ac.max_auto_route_level, 1)

    def test_auto_routable_level_2(self):
        ac = self._make("Medium Risk Auto", "auto_routable", max_level=2)
        self.assertEqual(ac.max_auto_route_level, 2)

    def test_auto_routable_negative_level_raises(self):
        with self.assertRaises(ValidationError):
            self._make("Negative Level", "auto_routable", max_level=-1)

    # ---- Class type transitions ----

    def test_changing_class_type_recomputes_approval(self):
        ac = self._make("Type Switcher", "advisory")
        self.assertFalse(ac.requires_approval)
        ac.write({"class_type": "approval_gated"})
        self.assertTrue(ac.requires_approval)

    # ---- Uniqueness ----

    def test_class_name_unique(self):
        self._make("Unique Class", "advisory")
        with self.assertRaises(Exception):
            self._make("Unique Class", "auto_routable")
