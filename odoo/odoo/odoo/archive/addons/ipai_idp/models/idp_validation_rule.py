# -*- coding: utf-8 -*-
"""
IDP Validation Rule Model.

Configurable validation rules for extraction results.
"""
import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpValidationRule(models.Model):
    """
    IDP Validation Rule.

    Defines validation rules that can be applied to extraction results.
    Supports various rule types for field validation.

    Rule Types:
        - required: Field must be present and non-null
        - format: Field must match regex pattern
        - range: Numeric field must be within range
        - sum_check: Total must equal sum of components
        - date_order: Date comparisons
        - custom: Python expression evaluation

    Attributes:
        _name: idp.validation.rule
        _description: IDP Validation Rule
    """

    _name = "idp.validation.rule"
    _description = "IDP Validation Rule"
    _order = "sequence, name"

    # Core fields
    name = fields.Char(
        string="Rule Name",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    # Targeting
    doc_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("receipt", "Receipt"),
            ("purchase_order", "Purchase Order"),
            ("delivery_note", "Delivery Note"),
            ("all", "All Document Types"),
        ],
        string="Document Type",
        default="all",
        required=True,
    )

    # Rule configuration
    rule_type = fields.Selection(
        [
            ("required", "Required Field"),
            ("format", "Format Check (Regex)"),
            ("range", "Numeric Range"),
            ("sum_check", "Sum Validation"),
            ("date_order", "Date Order"),
            ("in_list", "Value in List"),
            ("custom", "Custom Expression"),
        ],
        string="Rule Type",
        required=True,
    )
    field_name = fields.Char(
        string="Field Name",
        help="JSON path to the field (e.g., 'vendor_name', 'line_items.0.amount')",
    )

    # Rule parameters
    regex_pattern = fields.Char(
        string="Regex Pattern",
        help="Regular expression for format validation",
    )
    min_value = fields.Float(
        string="Min Value",
        help="Minimum value for range validation",
    )
    max_value = fields.Float(
        string="Max Value",
        help="Maximum value for range validation",
    )
    sum_fields = fields.Char(
        string="Sum Fields",
        help="Comma-separated list of fields to sum (e.g., 'subtotal,tax')",
    )
    total_field = fields.Char(
        string="Total Field",
        help="Field that should equal the sum",
    )
    date_field_1 = fields.Char(
        string="First Date Field",
    )
    date_field_2 = fields.Char(
        string="Second Date Field",
    )
    date_comparison = fields.Selection(
        [
            ("before", "First Before Second"),
            ("after", "First After Second"),
            ("equal", "Dates Equal"),
        ],
        string="Date Comparison",
    )
    allowed_values = fields.Char(
        string="Allowed Values",
        help="Comma-separated list of allowed values",
    )
    custom_expression = fields.Text(
        string="Custom Expression",
        help="Python expression. Use 'data' for extracted data dict. "
        "Return True for pass, False for fail.",
    )

    # Severity and behavior
    severity = fields.Selection(
        [
            ("error", "Error (blocks approval)"),
            ("warning", "Warning (allows approval)"),
            ("info", "Info (notification only)"),
        ],
        string="Severity",
        default="error",
        required=True,
    )
    error_message = fields.Char(
        string="Error Message",
        help="Custom error message to display on failure",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    def validate(self, data):
        """
        Execute this validation rule against extracted data.

        Args:
            data: dict of extracted data

        Returns:
            dict: {
                'passed': bool,
                'message': str,
                'severity': str
            }
        """
        self.ensure_one()
        result = {
            "passed": True,
            "message": "",
            "severity": self.severity,
            "rule_name": self.name,
        }

        try:
            if self.rule_type == "required":
                result = self._validate_required(data)
            elif self.rule_type == "format":
                result = self._validate_format(data)
            elif self.rule_type == "range":
                result = self._validate_range(data)
            elif self.rule_type == "sum_check":
                result = self._validate_sum(data)
            elif self.rule_type == "date_order":
                result = self._validate_date_order(data)
            elif self.rule_type == "in_list":
                result = self._validate_in_list(data)
            elif self.rule_type == "custom":
                result = self._validate_custom(data)

            result["severity"] = self.severity
            result["rule_name"] = self.name

        except Exception as e:
            _logger.exception("Validation rule %s failed with error", self.name)
            result = {
                "passed": False,
                "message": f"Rule execution error: {str(e)}",
                "severity": "error",
                "rule_name": self.name,
            }

        return result

    def _get_field_value(self, data, field_path):
        """
        Get a value from nested dict using dot notation.

        Args:
            data: The data dict
            field_path: Dot-notation path (e.g., 'line_items.0.amount')

        Returns:
            The value at the path, or None if not found
        """
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                try:
                    value = value[int(key)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return value

    def _validate_required(self, data):
        """Check if required field is present and non-null."""
        value = self._get_field_value(data, self.field_name)
        if value is None or value == "":
            return {
                "passed": False,
                "message": self.error_message
                or f"Required field '{self.field_name}' is missing or empty",
            }
        return {"passed": True, "message": ""}

    def _validate_format(self, data):
        """Check if field matches regex pattern."""
        value = self._get_field_value(data, self.field_name)
        if value is None:
            return {"passed": True, "message": ""}  # Skip if not present

        if not re.match(self.regex_pattern, str(value)):
            return {
                "passed": False,
                "message": self.error_message
                or f"Field '{self.field_name}' does not match required format",
            }
        return {"passed": True, "message": ""}

    def _validate_range(self, data):
        """Check if numeric field is within range."""
        value = self._get_field_value(data, self.field_name)
        if value is None:
            return {"passed": True, "message": ""}

        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return {
                "passed": False,
                "message": f"Field '{self.field_name}' is not a valid number",
            }

        if self.min_value is not None and num_value < self.min_value:
            return {
                "passed": False,
                "message": self.error_message
                or f"Field '{self.field_name}' is below minimum ({self.min_value})",
            }
        if self.max_value is not None and num_value > self.max_value:
            return {
                "passed": False,
                "message": self.error_message
                or f"Field '{self.field_name}' exceeds maximum ({self.max_value})",
            }
        return {"passed": True, "message": ""}

    def _validate_sum(self, data):
        """Validate that total equals sum of components."""
        if not self.sum_fields or not self.total_field:
            return {"passed": True, "message": ""}

        total_value = self._get_field_value(data, self.total_field)
        if total_value is None:
            return {"passed": True, "message": ""}

        try:
            total_value = float(total_value)
        except (ValueError, TypeError):
            return {
                "passed": False,
                "message": f"Total field '{self.total_field}' is not a valid number",
            }

        sum_value = 0.0
        for field in self.sum_fields.split(","):
            field = field.strip()
            val = self._get_field_value(data, field)
            if val is not None:
                try:
                    sum_value += float(val)
                except (ValueError, TypeError):
                    pass

        # Allow small floating point differences
        if abs(total_value - sum_value) > 0.01:
            return {
                "passed": False,
                "message": self.error_message
                or f"Sum check failed: {self.sum_fields} = {sum_value}, "
                f"but {self.total_field} = {total_value}",
            }
        return {"passed": True, "message": ""}

    def _validate_date_order(self, data):
        """Validate date ordering."""
        date1 = self._get_field_value(data, self.date_field_1)
        date2 = self._get_field_value(data, self.date_field_2)

        if not date1 or not date2:
            return {"passed": True, "message": ""}

        try:
            d1 = fields.Date.from_string(date1)
            d2 = fields.Date.from_string(date2)
        except (ValueError, TypeError):
            return {
                "passed": False,
                "message": "Invalid date format in date comparison",
            }

        if self.date_comparison == "before" and d1 >= d2:
            return {
                "passed": False,
                "message": self.error_message
                or f"{self.date_field_1} must be before {self.date_field_2}",
            }
        elif self.date_comparison == "after" and d1 <= d2:
            return {
                "passed": False,
                "message": self.error_message
                or f"{self.date_field_1} must be after {self.date_field_2}",
            }
        elif self.date_comparison == "equal" and d1 != d2:
            return {
                "passed": False,
                "message": self.error_message
                or f"{self.date_field_1} must equal {self.date_field_2}",
            }

        return {"passed": True, "message": ""}

    def _validate_in_list(self, data):
        """Check if value is in allowed list."""
        value = self._get_field_value(data, self.field_name)
        if value is None:
            return {"passed": True, "message": ""}

        allowed = [v.strip() for v in self.allowed_values.split(",")]
        if str(value) not in allowed:
            return {
                "passed": False,
                "message": self.error_message
                or f"Field '{self.field_name}' value '{value}' not in allowed values",
            }
        return {"passed": True, "message": ""}

    def _validate_custom(self, data):
        """Execute custom Python expression."""
        if not self.custom_expression:
            return {"passed": True, "message": ""}

        try:
            # Limited safe execution context
            result = eval(
                self.custom_expression,
                {"__builtins__": {}},
                {"data": data, "len": len, "sum": sum, "abs": abs},
            )
            if not result:
                return {
                    "passed": False,
                    "message": self.error_message or "Custom validation failed",
                }
            return {"passed": True, "message": ""}
        except Exception as e:
            return {
                "passed": False,
                "message": f"Custom expression error: {str(e)}",
            }

    @api.model
    def get_rules_for_doc_type(self, doc_type):
        """
        Get all active rules applicable to a document type.

        Args:
            doc_type: The document type

        Returns:
            recordset of idp.validation.rule
        """
        return self.search(
            [
                ("active", "=", True),
                ("doc_type", "in", [doc_type, "all"]),
            ],
            order="sequence",
        )
