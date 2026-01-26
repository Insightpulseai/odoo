#!/usr/bin/env python3
"""
Deterministic OCR extraction for expense receipts.

This is a stub implementation that can be swapped to PaddleOCR,
Tesseract, or cloud OCR services. The interface remains stable.

Usage:
    python ocr_extract.py --in receipt.txt --out result.json
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OCRResult:
    """Structured OCR extraction result."""

    merchant: Optional[str]
    receipt_date: Optional[str]
    total: Optional[float]
    confidence: float
    raw: Dict[str, Any]


# Regex patterns for receipt parsing
# Priority 1: "Total" keyword with currency
TOTAL_CURRENCY_RE = re.compile(
    r"(?i)\b(total|amount\s*due|grand\s*total)\b[^0-9]*(PHP|USD|\$|₱)?\s*"
    r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)"
)
# Priority 2: Just "Total" keyword
TOTAL_RE = re.compile(
    r"(?i)\b(total|amount\s*due|grand\s*total)\b[^0-9]*"
    r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)"
)
# Priority 3: Last currency amount in document (likely total)
CURRENCY_RE = re.compile(r"(?i)(PHP|USD|\$|₱)\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})")


def normalize_amount(amount_str: str) -> float:
    """Remove commas and convert to float."""
    return float(amount_str.replace(",", ""))


def parse_text(text: str) -> OCRResult:
    """
    Parse receipt text and extract structured data.

    Args:
        text: Raw text from OCR or text file

    Returns:
        OCRResult with extracted merchant, date, total, and confidence
    """
    merchant = None
    receipt_date = None
    total = None
    confidence = 0.0

    # Clean up text
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Heuristic: first non-empty, non-date line as merchant
    for line in lines[:5]:  # Check first 5 lines
        if not DATE_RE.search(line) and len(line) > 3:
            merchant = line[:80]  # Truncate long names
            break

    if merchant:
        confidence += 0.2

    # Extract total amount (priority order)
    # 1. Try "Total" keyword with currency (most reliable)
    total_currency_match = TOTAL_CURRENCY_RE.search(text)
    if total_currency_match:
        total = normalize_amount(total_currency_match.group(3))
        confidence += 0.4
    else:
        # 2. Try "Total" keyword without currency
        total_match = TOTAL_RE.search(text)
        if total_match:
            total = normalize_amount(total_match.group(2))
            confidence += 0.4
        else:
            # 3. Fallback: find last currency amount (often the total)
            currency_matches = list(CURRENCY_RE.finditer(text))
            if currency_matches:
                # Use the last match as it's often the total
                last_match = currency_matches[-1]
                total = normalize_amount(last_match.group(2))
                confidence += 0.3  # Lower confidence for this heuristic

    # Extract date
    date_match = DATE_RE.search(text)
    if date_match:
        date_str = date_match.group(1)
        # Normalize to ISO format
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts[2]) == 4:  # MM/DD/YYYY
                receipt_date = f"{parts[2]}-{parts[0]:>02}-{parts[1]:>02}"
            else:  # DD/MM/YY or similar
                receipt_date = date_str
        elif "-" in date_str and len(date_str) == 10:
            receipt_date = date_str
        else:
            receipt_date = date_str
        confidence += 0.2

    # Bonus confidence if we found multiple fields
    if merchant and total and receipt_date:
        confidence = min(confidence + 0.2, 1.0)

    return OCRResult(
        merchant=merchant,
        receipt_date=receipt_date,
        total=total,
        confidence=round(confidence, 2),
        raw={"text": text, "lines": lines},
    )


def main():
    """CLI entrypoint for OCR extraction."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract structured data from receipt text")
    parser.add_argument("--in", dest="infile", required=True, help="Input text file")
    parser.add_argument("--out", dest="outfile", required=True, help="Output JSON file")
    args = parser.parse_args()

    # Read input
    with open(args.infile, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse
    result = parse_text(text)

    # Write output
    output = {
        "merchant": result.merchant,
        "receipt_date": result.receipt_date,
        "total": result.total,
        "confidence": result.confidence,
        "raw": result.raw,
    }

    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(output, ensure_ascii=False, indent=2, fp=f)

    print(f"Extracted: merchant={result.merchant}, total={result.total}, date={result.receipt_date}")
    print(f"Confidence: {result.confidence:.0%}")


if __name__ == "__main__":
    main()
