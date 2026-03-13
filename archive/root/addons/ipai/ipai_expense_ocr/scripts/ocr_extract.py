#!/usr/bin/env python3
"""
Deterministic OCR extraction for expense receipts.

Parsing logic lives in utils/ocr_client.py so it can be shared between
this CLI script and the Odoo model (models/hr_expense_mixin.py).

Usage:
    python ocr_extract.py --in receipt.txt --out result.json
"""

import json
import sys
import os

# Allow running as standalone script from scripts/ directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_ROOT = os.path.dirname(_SCRIPT_DIR)  # ipai_expense_ocr/
if _MODULE_ROOT not in sys.path:
    sys.path.insert(0, os.path.dirname(_MODULE_ROOT))  # addons/ipai/

from ipai_expense_ocr.utils.ocr_client import OCRResult, parse_text  # noqa: E402,F401


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
