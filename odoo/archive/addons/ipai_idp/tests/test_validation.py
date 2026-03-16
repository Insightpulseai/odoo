# -*- coding: utf-8 -*-
"""
Unit Tests for IDP Validation Rules.

Tests validation rule engine including:
- Required field validation
- Format validation (regex)
- Range validation
- Sum check validation
- Date order validation
- Custom expression validation
"""
from odoo.tests.common import TransactionCase


class TestIdpValidation(TransactionCase):
    """Test cases for idp.validation.rule."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.ValidationRule = cls.env["idp.validation.rule"]

    # ==================== Required Field Tests ====================

    def test_required_field_present(self):
        """Test required field validation when field is present."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Required",
                "rule_type": "required",
                "field_name": "vendor_name",
                "severity": "error",
            }
        )

        data = {"vendor_name": "Test Vendor", "total": 100.00}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_required_field_missing(self):
        """Test required field validation when field is missing."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Required",
                "rule_type": "required",
                "field_name": "vendor_name",
                "severity": "error",
            }
        )

        data = {"total": 100.00}
        result = rule.validate(data)

        self.assertFalse(result["passed"])
        self.assertEqual(result["severity"], "error")

    def test_required_field_empty(self):
        """Test required field validation when field is empty."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Required",
                "rule_type": "required",
                "field_name": "vendor_name",
                "severity": "error",
            }
        )

        data = {"vendor_name": "", "total": 100.00}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    # ==================== Format Validation Tests ====================

    def test_format_valid(self):
        """Test format validation with valid input."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Format",
                "rule_type": "format",
                "field_name": "invoice_date",
                "regex_pattern": r"^\d{4}-\d{2}-\d{2}$",
                "severity": "warning",
            }
        )

        data = {"invoice_date": "2024-12-06"}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_format_invalid(self):
        """Test format validation with invalid input."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Format",
                "rule_type": "format",
                "field_name": "invoice_date",
                "regex_pattern": r"^\d{4}-\d{2}-\d{2}$",
                "severity": "warning",
            }
        )

        data = {"invoice_date": "12/06/2024"}
        result = rule.validate(data)

        self.assertFalse(result["passed"])
        self.assertEqual(result["severity"], "warning")

    def test_format_field_missing(self):
        """Test format validation skips when field is missing."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Format",
                "rule_type": "format",
                "field_name": "invoice_date",
                "regex_pattern": r"^\d{4}-\d{2}-\d{2}$",
                "severity": "warning",
            }
        )

        data = {"vendor_name": "Test"}
        result = rule.validate(data)

        self.assertTrue(result["passed"])  # Skips validation

    # ==================== Range Validation Tests ====================

    def test_range_within_bounds(self):
        """Test range validation within bounds."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Range",
                "rule_type": "range",
                "field_name": "total",
                "min_value": 0.01,
                "max_value": 1000000,
                "severity": "error",
            }
        )

        data = {"total": 500.00}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_range_below_minimum(self):
        """Test range validation below minimum."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Range",
                "rule_type": "range",
                "field_name": "total",
                "min_value": 0.01,
                "severity": "error",
            }
        )

        data = {"total": 0}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    def test_range_above_maximum(self):
        """Test range validation above maximum."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Range",
                "rule_type": "range",
                "field_name": "total",
                "max_value": 1000,
                "severity": "error",
            }
        )

        data = {"total": 1500}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    # ==================== Sum Check Tests ====================

    def test_sum_check_valid(self):
        """Test sum check validation when totals match."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Sum",
                "rule_type": "sum_check",
                "sum_fields": "subtotal, tax",
                "total_field": "total",
                "severity": "error",
            }
        )

        data = {"subtotal": 90.00, "tax": 10.00, "total": 100.00}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_sum_check_invalid(self):
        """Test sum check validation when totals don't match."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Sum",
                "rule_type": "sum_check",
                "sum_fields": "subtotal, tax",
                "total_field": "total",
                "severity": "error",
            }
        )

        data = {"subtotal": 90.00, "tax": 10.00, "total": 150.00}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    def test_sum_check_with_floating_point(self):
        """Test sum check handles floating point precision."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Sum",
                "rule_type": "sum_check",
                "sum_fields": "subtotal, tax",
                "total_field": "total",
                "severity": "error",
            }
        )

        # These may have floating point issues: 0.1 + 0.2 != 0.3
        data = {"subtotal": 0.1, "tax": 0.2, "total": 0.3}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    # ==================== Date Order Tests ====================

    def test_date_order_valid(self):
        """Test date order validation when order is correct."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Date Order",
                "rule_type": "date_order",
                "date_field_1": "invoice_date",
                "date_field_2": "due_date",
                "date_comparison": "before",
                "severity": "warning",
            }
        )

        data = {"invoice_date": "2024-12-01", "due_date": "2024-12-31"}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_date_order_invalid(self):
        """Test date order validation when order is wrong."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Date Order",
                "rule_type": "date_order",
                "date_field_1": "invoice_date",
                "date_field_2": "due_date",
                "date_comparison": "before",
                "severity": "warning",
            }
        )

        data = {"invoice_date": "2024-12-31", "due_date": "2024-12-01"}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    # ==================== In List Tests ====================

    def test_in_list_valid(self):
        """Test in list validation with valid value."""
        rule = self.ValidationRule.create(
            {
                "name": "Test In List",
                "rule_type": "in_list",
                "field_name": "currency",
                "allowed_values": "PHP, USD, EUR, GBP",
                "severity": "error",
            }
        )

        data = {"currency": "PHP"}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_in_list_invalid(self):
        """Test in list validation with invalid value."""
        rule = self.ValidationRule.create(
            {
                "name": "Test In List",
                "rule_type": "in_list",
                "field_name": "currency",
                "allowed_values": "PHP, USD, EUR, GBP",
                "severity": "error",
            }
        )

        data = {"currency": "XYZ"}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    # ==================== Custom Expression Tests ====================

    def test_custom_expression_valid(self):
        """Test custom expression validation that passes."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Custom",
                "rule_type": "custom",
                "custom_expression": "data.get('total', 0) > 0",
                "severity": "error",
            }
        )

        data = {"total": 100.00}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    def test_custom_expression_invalid(self):
        """Test custom expression validation that fails."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Custom",
                "rule_type": "custom",
                "custom_expression": "data.get('total', 0) > 0",
                "severity": "error",
            }
        )

        data = {"total": 0}
        result = rule.validate(data)

        self.assertFalse(result["passed"])

    def test_custom_expression_complex(self):
        """Test complex custom expression."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Custom Complex",
                "rule_type": "custom",
                "custom_expression": "len(data.get('line_items', [])) > 0",
                "severity": "warning",
            }
        )

        data = {"line_items": [{"description": "Item 1", "amount": 50}]}
        result = rule.validate(data)

        self.assertTrue(result["passed"])

    # ==================== Nested Field Tests ====================

    def test_nested_field_value(self):
        """Test accessing nested field values."""
        rule = self.ValidationRule.create(
            {
                "name": "Test Nested",
                "rule_type": "required",
                "field_name": "line_items.0.description",
                "severity": "warning",
            }
        )

        data = {"line_items": [{"description": "Item 1", "amount": 50}]}
        result = rule.validate(data)

        self.assertTrue(result["passed"])


class TestIdpValidationService(TransactionCase):
    """Test cases for idp.service.validator."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.validator = cls.env["idp.service.validator"]
        cls.ValidationRule = cls.env["idp.validation.rule"]

    def test_validate_data_pass(self):
        """Test validation service with passing data."""
        # Create a rule
        self.ValidationRule.create(
            {
                "name": "Vendor Required",
                "rule_type": "required",
                "field_name": "vendor_name",
                "doc_type": "all",
                "severity": "error",
            }
        )

        data = {"vendor_name": "Test Vendor", "total": 100.00}
        result = self.validator.validate_data(data, "invoice")

        self.assertEqual(result["status"], "pass")
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_data_fail(self):
        """Test validation service with failing data."""
        # Create a rule
        self.ValidationRule.create(
            {
                "name": "Vendor Required",
                "rule_type": "required",
                "field_name": "vendor_name",
                "doc_type": "all",
                "severity": "error",
            }
        )

        data = {"total": 100.00}
        result = self.validator.validate_data(data, "invoice")

        self.assertEqual(result["status"], "fail")
        self.assertGreater(len(result["errors"]), 0)

    def test_validate_data_warning(self):
        """Test validation service with warnings."""
        # Create a warning rule
        self.ValidationRule.create(
            {
                "name": "Date Format",
                "rule_type": "format",
                "field_name": "invoice_date",
                "regex_pattern": r"^\d{4}-\d{2}-\d{2}$",
                "doc_type": "all",
                "severity": "warning",
            }
        )

        data = {"invoice_date": "12/06/2024", "vendor_name": "Test"}
        result = self.validator.validate_data(data, "invoice")

        self.assertEqual(result["status"], "warning")
        self.assertGreater(len(result["warnings"]), 0)
