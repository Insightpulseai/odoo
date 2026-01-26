"""Unit tests for OCR extraction."""

import sys
from pathlib import Path

# Add module to path for direct test execution
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ocr_extract import parse_text, normalize_amount


def test_parse_text_full_receipt():
    """Test parsing a complete receipt with all fields."""
    txt = """ACME STORE
123 Main Street
Date: 2026-01-25

Item 1          PHP 50.00
Item 2          PHP 73.45

Total PHP 123.45
"""
    result = parse_text(txt)
    assert result.merchant == "ACME STORE"
    assert result.receipt_date == "2026-01-25"
    assert result.total == 123.45
    assert result.confidence >= 0.8


def test_parse_text_minimal():
    """Test parsing receipt with minimal info."""
    txt = """Some Store
Total: 99.99
"""
    result = parse_text(txt)
    assert result.merchant == "Some Store"
    assert result.total == 99.99
    assert result.confidence >= 0.4


def test_parse_text_with_commas():
    """Test parsing amounts with thousand separators."""
    txt = """Big Purchase Store
Grand Total: 1,234.56
"""
    result = parse_text(txt)
    assert result.total == 1234.56


def test_parse_text_currency_symbol():
    """Test parsing with currency symbols."""
    txt = """Coffee Shop
₱ 150.00
"""
    result = parse_text(txt)
    assert result.total == 150.0


def test_parse_text_usd():
    """Test parsing USD amounts."""
    txt = """US Store
Total: $99.99
"""
    result = parse_text(txt)
    assert result.total == 99.99


def test_parse_text_date_formats():
    """Test various date formats."""
    # ISO format
    txt1 = "Store\n2026-01-25\nTotal 100"
    r1 = parse_text(txt1)
    assert r1.receipt_date == "2026-01-25"

    # US format
    txt2 = "Store\n01/25/2026\nTotal 100"
    r2 = parse_text(txt2)
    assert "2026" in r2.receipt_date


def test_normalize_amount():
    """Test amount normalization."""
    assert normalize_amount("1,234.56") == 1234.56
    assert normalize_amount("100.00") == 100.0
    assert normalize_amount("1,000,000.00") == 1000000.0


def test_parse_text_no_merchant():
    """Test parsing when merchant detection fails."""
    txt = """2026-01-25
Total 50.00
"""
    result = parse_text(txt)
    # Date line should not be merchant
    assert result.total == 50.0


def test_parse_text_empty():
    """Test parsing empty text."""
    result = parse_text("")
    assert result.merchant is None
    assert result.total is None
    assert result.receipt_date is None
    assert result.confidence == 0.0


if __name__ == "__main__":
    # Run tests directly
    import pytest
    pytest.main([__file__, "-v"])
