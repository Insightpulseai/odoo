"""
OCR client utilities for expense receipt digitization.

Provides two main functions:
- parse_text(): regex-parse raw receipt text → structured OCRResult
- fetch_image_text(): POST image bytes to PaddleOCR FastAPI endpoint → raw text

Importable from both the CLI script (ocr_extract.py) and Odoo models (hr_expense_mixin.py).
"""

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


# ---------------------------------------------------------------------------
# Regex patterns for receipt parsing
# ---------------------------------------------------------------------------

# Priority 1: "Total" keyword with currency (most reliable)
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

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Heuristic: first non-empty, non-date line as merchant
    for line in lines[:5]:
        if not DATE_RE.search(line) and len(line) > 3:
            merchant = line[:80]
            break

    if merchant:
        confidence += 0.2

    # Extract total amount (priority order)
    total_currency_match = TOTAL_CURRENCY_RE.search(text)
    if total_currency_match:
        total = normalize_amount(total_currency_match.group(3))
        confidence += 0.4
    else:
        total_match = TOTAL_RE.search(text)
        if total_match:
            total = normalize_amount(total_match.group(2))
            confidence += 0.4
        else:
            currency_matches = list(CURRENCY_RE.finditer(text))
            if currency_matches:
                last_match = currency_matches[-1]
                total = normalize_amount(last_match.group(2))
                confidence += 0.3

    # Extract date
    date_match = DATE_RE.search(text)
    if date_match:
        date_str = date_match.group(1)
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts[2]) == 4:  # MM/DD/YYYY
                receipt_date = f"{parts[2]}-{parts[0]:>02}-{parts[1]:>02}"
            else:
                receipt_date = date_str
        elif "-" in date_str and len(date_str) == 10:
            receipt_date = date_str
        else:
            receipt_date = date_str
        confidence += 0.2

    # Bonus if all three fields found
    if merchant and total and receipt_date:
        confidence = min(confidence + 0.2, 1.0)

    return OCRResult(
        merchant=merchant,
        receipt_date=receipt_date,
        total=total,
        confidence=round(confidence, 2),
        raw={"text": text, "lines": lines},
    )


def fetch_image_text(image_bytes: bytes, endpoint_url: str) -> str:
    """
    POST image bytes to PaddleOCR FastAPI /ocr endpoint, return extracted raw text.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, etc.)
        endpoint_url: Base URL of the OCR service (e.g. https://ocr.insightpulseai.com)

    Returns:
        Extracted text string from OCR

    Raises:
        requests.RequestException: On network error, timeout, or HTTP error
    """
    import requests  # lazy import — not available in all contexts

    url = f"{endpoint_url.rstrip('/')}/ocr"
    resp = requests.post(
        url,
        files={"file": ("receipt.jpg", image_bytes, "image/jpeg")},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # ocr_service/server.py returns {"text": "...", "lines": [...], "confidence": 0.xx}
    return data.get("text") or "\n".join(
        line.get("text", "") for line in data.get("lines", [])
    )
