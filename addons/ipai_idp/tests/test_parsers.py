# -*- coding: utf-8 -*-
"""
Unit Tests for IDP Parser Service.

Tests text parsing utilities including:
- Amount parsing with various formats
- Currency detection
- Date normalization
- Text cleaning
"""
from odoo.tests.common import TransactionCase


class TestIdpParser(TransactionCase):
    """Test cases for idp.service.parser."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.parser = cls.env["idp.service.parser"]

    # ==================== Amount Parsing Tests ====================

    def test_parse_amount_simple(self):
        """Test parsing simple numeric amount."""
        result = self.parser.parse_amount("1234.50")
        self.assertEqual(result, 1234.50)

    def test_parse_amount_with_peso_symbol(self):
        """Test parsing amount with Philippine Peso symbol."""
        result = self.parser.parse_amount("₱1,234.50")
        self.assertEqual(result, 1234.50)

    def test_parse_amount_with_dollar_symbol(self):
        """Test parsing amount with dollar symbol."""
        result = self.parser.parse_amount("$1,234.50")
        self.assertEqual(result, 1234.50)

    def test_parse_amount_with_euro_symbol(self):
        """Test parsing amount with Euro symbol."""
        result = self.parser.parse_amount("€1.234,50")
        self.assertEqual(result, 1234.50)

    def test_parse_amount_with_spaces(self):
        """Test parsing amount with leading/trailing spaces."""
        result = self.parser.parse_amount("  2,000.00  ")
        self.assertEqual(result, 2000.00)

    def test_parse_amount_no_decimals(self):
        """Test parsing integer amount."""
        result = self.parser.parse_amount("1,000")
        self.assertEqual(result, 1000.0)

    def test_parse_amount_negative(self):
        """Test parsing negative amount."""
        result = self.parser.parse_amount("-500.00")
        self.assertEqual(result, -500.00)

    def test_parse_amount_parentheses_negative(self):
        """Test parsing negative amount in parentheses."""
        result = self.parser.parse_amount("(500.00)")
        self.assertEqual(result, -500.00)

    def test_parse_amount_empty(self):
        """Test parsing empty string returns None."""
        result = self.parser.parse_amount("")
        self.assertIsNone(result)

    def test_parse_amount_none(self):
        """Test parsing None returns None."""
        result = self.parser.parse_amount(None)
        self.assertIsNone(result)

    def test_parse_amount_european_format(self):
        """Test parsing European format (1.234,50)."""
        result = self.parser.parse_amount("1.234,50")
        self.assertEqual(result, 1234.50)

    def test_parse_amount_large_number(self):
        """Test parsing large number with multiple separators."""
        result = self.parser.parse_amount("1,234,567.89")
        self.assertEqual(result, 1234567.89)

    # ==================== Currency Parsing Tests ====================

    def test_parse_currency_peso_symbol(self):
        """Test detecting PHP from peso symbol."""
        result = self.parser.parse_currency("₱1,234.50")
        self.assertEqual(result, "PHP")

    def test_parse_currency_dollar_symbol(self):
        """Test detecting USD from dollar symbol."""
        result = self.parser.parse_currency("$100.00")
        self.assertEqual(result, "USD")

    def test_parse_currency_euro_symbol(self):
        """Test detecting EUR from euro symbol."""
        result = self.parser.parse_currency("€50.00")
        self.assertEqual(result, "EUR")

    def test_parse_currency_code_explicit(self):
        """Test detecting currency from explicit code."""
        result = self.parser.parse_currency("USD")
        self.assertEqual(result, "USD")

    def test_parse_currency_code_in_text(self):
        """Test extracting currency code from text."""
        result = self.parser.parse_currency("Total: 100 PHP")
        self.assertEqual(result, "PHP")

    def test_parse_currency_empty(self):
        """Test empty string returns None."""
        result = self.parser.parse_currency("")
        self.assertIsNone(result)

    # ==================== Amount with Currency Tests ====================

    def test_parse_amount_with_currency_peso(self):
        """Test parsing amount and currency together."""
        amount, currency = self.parser.parse_amount_with_currency("₱1,234.50")
        self.assertEqual(amount, 1234.50)
        self.assertEqual(currency, "PHP")

    def test_parse_amount_with_currency_usd(self):
        """Test parsing USD amount."""
        amount, currency = self.parser.parse_amount_with_currency("$99.99")
        self.assertEqual(amount, 99.99)
        self.assertEqual(currency, "USD")

    # ==================== Date Normalization Tests ====================

    def test_normalize_date_iso_format(self):
        """Test normalizing ISO date format."""
        result = self.parser.normalize_date("2024-12-06")
        self.assertEqual(result, "2024-12-06")

    def test_normalize_date_us_format(self):
        """Test normalizing US date format."""
        result = self.parser.normalize_date("12/06/2024")
        self.assertEqual(result, "2024-12-06")

    def test_normalize_date_european_format(self):
        """Test normalizing European date format."""
        result = self.parser.normalize_date("06.12.2024")
        self.assertEqual(result, "2024-12-06")

    def test_normalize_date_text_format(self):
        """Test normalizing text date format."""
        result = self.parser.normalize_date("06 Dec 2024")
        self.assertEqual(result, "2024-12-06")

    def test_normalize_date_text_format_full(self):
        """Test normalizing full text date format."""
        result = self.parser.normalize_date("December 6, 2024")
        # Should handle this format
        self.assertIsNotNone(result)

    def test_normalize_date_empty(self):
        """Test empty string returns None."""
        result = self.parser.normalize_date("")
        self.assertIsNone(result)

    def test_normalize_date_invalid(self):
        """Test invalid date returns None."""
        result = self.parser.normalize_date("not a date")
        self.assertIsNone(result)

    # ==================== Text Cleaning Tests ====================

    def test_clean_text_extra_whitespace(self):
        """Test removing extra whitespace."""
        result = self.parser.clean_text("  Hello   World  ")
        self.assertEqual(result, "Hello World")

    def test_clean_text_multiple_newlines(self):
        """Test normalizing multiple newlines."""
        result = self.parser.clean_text("Line 1\n\n\n\nLine 2")
        self.assertEqual(result, "Line 1\n\nLine 2")

    def test_clean_text_crlf(self):
        """Test normalizing CRLF line endings."""
        result = self.parser.clean_text("Line 1\r\nLine 2")
        self.assertEqual(result, "Line 1\nLine 2")

    def test_clean_text_empty(self):
        """Test empty string returns empty."""
        result = self.parser.clean_text("")
        self.assertEqual(result, "")

    def test_clean_text_none(self):
        """Test None returns empty."""
        result = self.parser.clean_text(None)
        self.assertEqual(result, "")

    # ==================== Invoice Number Extraction Tests ====================

    def test_extract_invoice_number_standard(self):
        """Test extracting standard invoice number."""
        text = "Invoice No: INV-2024-001\nTotal: $100.00"
        result = self.parser.extract_invoice_number(text)
        self.assertEqual(result, "INV-2024-001")

    def test_extract_invoice_number_hash(self):
        """Test extracting invoice number with hash."""
        text = "Invoice #12345\nTotal: $100.00"
        result = self.parser.extract_invoice_number(text)
        self.assertEqual(result, "12345")

    def test_extract_invoice_number_reference(self):
        """Test extracting reference number."""
        text = "Reference: REF-001\nAmount: $50.00"
        result = self.parser.extract_invoice_number(text)
        self.assertEqual(result, "REF-001")

    def test_extract_invoice_number_not_found(self):
        """Test when no invoice number found."""
        text = "Random text without invoice number"
        result = self.parser.extract_invoice_number(text)
        self.assertIsNone(result)

    # ==================== Total Amount Extraction Tests ====================

    def test_extract_total_amount_standard(self):
        """Test extracting standard total."""
        text = "Subtotal: $90.00\nTax: $10.00\nTotal: $100.00"
        amount, currency = self.parser.extract_total_amount(text)
        self.assertEqual(amount, 100.00)
        self.assertEqual(currency, "USD")

    def test_extract_total_amount_grand_total(self):
        """Test extracting grand total."""
        text = "Subtotal: $90.00\nGrand Total: ₱1,234.50"
        amount, currency = self.parser.extract_total_amount(text)
        self.assertEqual(amount, 1234.50)
        self.assertEqual(currency, "PHP")

    def test_extract_total_amount_not_found(self):
        """Test when no total found."""
        text = "Some random text"
        amount, currency = self.parser.extract_total_amount(text)
        self.assertIsNone(amount)
        self.assertIsNone(currency)
