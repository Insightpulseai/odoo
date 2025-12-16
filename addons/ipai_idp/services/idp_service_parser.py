# -*- coding: utf-8 -*-
"""
IDP Parser Service.

Text parsing utilities for normalizing OCR output and extracted values.
"""
import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from odoo import api, models

_logger = logging.getLogger(__name__)


# Currency symbol to ISO code mapping
CURRENCY_SYMBOLS = {
    "$": "USD",
    "₱": "PHP",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "₩": "KRW",
    "฿": "THB",
    "₫": "VND",
    "₴": "UAH",
    "₪": "ILS",
    "₺": "TRY",
    "₽": "RUB",
    "R$": "BRL",
    "S$": "SGD",
    "HK$": "HKD",
    "A$": "AUD",
    "C$": "CAD",
    "NZ$": "NZD",
    "CHF": "CHF",
    "kr": "SEK",  # Also NOK, DKK
    "zł": "PLN",
    "Kč": "CZK",
    "RM": "MYR",
    "Rp": "IDR",
}

# Common date format patterns
DATE_PATTERNS = [
    # ISO format
    (r"(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
    # US format
    (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%m/%d/%Y"),
    (r"(\d{1,2})/(\d{1,2})/(\d{2})", "%m/%d/%y"),
    # European format
    (r"(\d{1,2})\.(\d{1,2})\.(\d{4})", "%d.%m.%Y"),
    (r"(\d{1,2})-(\d{1,2})-(\d{4})", "%d-%m-%Y"),
    # Text formats
    (r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})", None),
    (
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})",
        None,
    ),
]


class IdpServiceParser(models.AbstractModel):
    """
    IDP Text Parsing Service.

    Provides utilities for:
    - Amount/currency parsing
    - Date normalization
    - Text cleaning
    - Field extraction helpers

    Attributes:
        _name: idp.service.parser
        _description: IDP Parser Service
    """

    _name = "idp.service.parser"
    _description = "IDP Parser Service"

    @api.model
    def parse_amount(self, text):
        """
        Parse an amount string into a float.

        Handles various formats:
        - "₱1,234.50" -> 1234.50
        - "1.234,50" (European) -> 1234.50
        - "$1,234" -> 1234.00
        - "1234.5" -> 1234.50

        Args:
            text: Amount string with optional currency symbol

        Returns:
            float: Parsed amount, or None if parsing fails
        """
        if not text:
            return None

        text = str(text).strip()

        # Remove currency symbols and whitespace
        for symbol in CURRENCY_SYMBOLS.keys():
            text = text.replace(symbol, "")
        text = text.strip()

        # Handle negative amounts
        is_negative = False
        if text.startswith("-") or text.startswith("("):
            is_negative = True
            text = text.strip("-()").strip()

        # Detect decimal separator
        # If both . and , exist, the last one is the decimal separator
        has_comma = "," in text
        has_dot = "." in text

        if has_comma and has_dot:
            # Find which comes last
            last_comma = text.rfind(",")
            last_dot = text.rfind(".")

            if last_comma > last_dot:
                # European format: 1.234,50
                text = text.replace(".", "").replace(",", ".")
            else:
                # US format: 1,234.50
                text = text.replace(",", "")
        elif has_comma:
            # Could be decimal or thousands separator
            # If there are exactly 2 digits after comma, treat as decimal
            parts = text.split(",")
            if len(parts) == 2 and len(parts[1]) <= 2:
                text = text.replace(",", ".")
            else:
                text = text.replace(",", "")
        # If only dot, leave as is

        try:
            amount = float(Decimal(text))
            return -amount if is_negative else amount
        except (InvalidOperation, ValueError) as e:
            _logger.debug("Failed to parse amount '%s': %s", text, e)
            return None

    @api.model
    def parse_currency(self, text):
        """
        Extract currency code from text.

        Args:
            text: Text containing currency symbol or code

        Returns:
            str: ISO 4217 currency code, or None
        """
        if not text:
            return None

        text = str(text).strip()

        # Check for explicit currency codes
        if len(text) == 3 and text.upper().isalpha():
            return text.upper()

        # Check for currency symbols
        for symbol, code in CURRENCY_SYMBOLS.items():
            if symbol in text:
                return code

        # Try to extract 3-letter code from text
        match = re.search(r"\b([A-Z]{3})\b", text.upper())
        if match:
            return match.group(1)

        return None

    @api.model
    def parse_amount_with_currency(self, text):
        """
        Parse amount and currency from a single string.

        Args:
            text: String like "₱1,234.50" or "USD 100.00"

        Returns:
            tuple: (amount: float, currency: str)
        """
        amount = self.parse_amount(text)
        currency = self.parse_currency(text)
        return (amount, currency)

    @api.model
    def normalize_date(self, text):
        """
        Normalize a date string to ISO format (YYYY-MM-DD).

        Handles various input formats.

        Args:
            text: Date string in various formats

        Returns:
            str: ISO format date string, or None
        """
        if not text:
            return None

        text = str(text).strip()

        # Month name mapping
        month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        # Try each pattern
        for pattern, fmt in DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()

                if fmt:
                    # Standard datetime parsing
                    try:
                        date_str = match.group(0)
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                else:
                    # Handle text month formats
                    try:
                        if groups[0].isdigit():
                            # "01 Dec 2024" format
                            day = int(groups[0])
                            month = month_map.get(groups[1].lower(), 0)
                            year = int(groups[2])
                        else:
                            # "Dec 01, 2024" format
                            month = month_map.get(groups[0].lower(), 0)
                            day = int(groups[1])
                            year = int(groups[2])

                        if month > 0:
                            dt = datetime(year, month, day)
                            return dt.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        continue

        # If no pattern matched, try generic parsing
        try:
            # Remove common suffixes
            text = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text, flags=re.IGNORECASE)

            # Try dateutil if available
            from dateutil import parser as dateutil_parser

            dt = dateutil_parser.parse(text, dayfirst=True)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

        _logger.debug("Failed to normalize date: '%s'", text)
        return None

    @api.model
    def clean_text(self, text):
        """
        Clean OCR text for better extraction.

        - Removes extra whitespace
        - Normalizes line endings
        - Fixes common OCR errors

        Args:
            text: Raw OCR text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        text = str(text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Normalize whitespace within lines
        lines = text.split("\n")
        lines = [" ".join(line.split()) for line in lines]
        text = "\n".join(lines)

        # Fix common OCR errors
        ocr_fixes = {
            r"\bl\b": "1",  # lowercase L to 1 in numeric context
            r"\bO\b": "0",  # uppercase O to 0 in numeric context
            r"lnvoice": "Invoice",
            r"Rece1pt": "Receipt",
            r"Arnount": "Amount",
            r"Tota1": "Total",
        }

        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)

        return text.strip()

    @api.model
    def extract_invoice_number(self, text):
        """
        Extract invoice number from text.

        Looks for common patterns like:
        - Invoice No: 12345
        - Inv# ABC-123
        - Reference: REF-2024-001

        Args:
            text: OCR text

        Returns:
            str: Extracted invoice number, or None
        """
        if not text:
            return None

        patterns = [
            r"(?:Invoice|Inv\.?|Bill)\s*(?:No\.?|Number|#|:)\s*:?\s*([A-Z0-9][\w\-\/]+)",
            r"(?:Reference|Ref\.?)\s*(?:No\.?|#|:)\s*:?\s*([A-Z0-9][\w\-\/]+)",
            r"(?:Document|Doc\.?)\s*(?:No\.?|#|:)\s*:?\s*([A-Z0-9][\w\-\/]+)",
            r"#\s*([A-Z0-9][\w\-\/]{3,})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @api.model
    def extract_vendor_name(self, text):
        """
        Extract vendor/merchant name from text.

        Typically appears at the top of the document.

        Args:
            text: OCR text

        Returns:
            str: Extracted vendor name, or None
        """
        if not text:
            return None

        lines = text.strip().split("\n")
        if not lines:
            return None

        # The first non-empty, non-address line is often the vendor name
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line:
                continue

            # Skip if it looks like an address
            if re.search(
                r"\b(street|st\.|ave|avenue|road|rd\.|blvd|city|state|zip|postal)\b",
                line,
                re.IGNORECASE,
            ):
                continue

            # Skip if it looks like a phone number or email
            if re.search(r"[\d\-\(\)]{10,}|@|\.[a-z]{2,4}\b", line, re.IGNORECASE):
                continue

            # Skip if it's a common header
            if re.search(
                r"^(invoice|receipt|bill|order|tax|date)\b", line, re.IGNORECASE
            ):
                continue

            # Return this line as the vendor name
            if len(line) >= 3:
                return line

        return None

    @api.model
    def extract_total_amount(self, text):
        """
        Extract total amount from text.

        Looks for patterns like:
        - Total: $1,234.50
        - Grand Total: 1234.50
        - Amount Due: ₱1,234.50

        Args:
            text: OCR text

        Returns:
            tuple: (amount: float, currency: str)
        """
        if not text:
            return (None, None)

        patterns = [
            r"(?:Grand\s+)?Total\s*:?\s*([\$₱€£¥]?\s*[\d,\.]+)",
            r"Amount\s+Due\s*:?\s*([\$₱€£¥]?\s*[\d,\.]+)",
            r"Balance\s+Due\s*:?\s*([\$₱€£¥]?\s*[\d,\.]+)",
            r"Net\s+Amount\s*:?\s*([\$₱€£¥]?\s*[\d,\.]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).strip()
                return self.parse_amount_with_currency(amount_str)

        return (None, None)
