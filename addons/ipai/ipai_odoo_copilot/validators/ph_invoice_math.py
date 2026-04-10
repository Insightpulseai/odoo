# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""PH Invoice Math Validator — pure Python, no Odoo dependencies.

Validates Philippine invoice arithmetic:
  - Line item sum == net_of_vat
  - net_of_vat * vat_rate == vat_amount (within tolerance)
  - net_of_vat + vat_amount == gross_total (within tolerance)
  - net_of_vat * withholding_rate == withholding_amount (within tolerance)
  - gross_total - withholding_amount == expected_payable
  - expected_payable == printed_total_due (within tolerance)

Returns a dict with status, expected_payable, printed_total_due, and findings.
"""

from decimal import ROUND_HALF_UP, Decimal

_TOLERANCE = Decimal("0.02")  # ₱0.02 rounding tolerance


def _dec(value):
    """Convert a numeric value to Decimal, rounding to 2 decimal places."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate(doc):
    """Validate Philippine invoice math.

    Args:
        doc: dict with invoice fields (see module docstring for keys).

    Returns:
        dict:
          status: 'validated' | 'needs_review'
          expected_payable: Decimal
          printed_total_due: Decimal
          findings: list of finding dicts
    """
    findings = []

    net_of_vat = _dec(doc.get("net_of_vat", 0))
    vat_rate = _dec(doc.get("vat_rate", 0))
    vat_amount = _dec(doc.get("vat_amount", 0))
    gross_total = _dec(doc.get("gross_total", 0))
    withholding_rate = _dec(doc.get("withholding_rate", 0))
    withholding_amount = _dec(doc.get("withholding_amount", 0))
    printed_total_due = _dec(doc.get("printed_total_due", 0))

    lines = doc.get("lines", [])

    # --- Check 1: line items sum ---
    if lines:
        line_sum = sum(_dec(ln.get("amount", 0)) for ln in lines)
        if abs(line_sum - net_of_vat) > _TOLERANCE:
            findings.append({
                "code": "LINE_SUM_MISMATCH",
                "expected": str(net_of_vat),
                "actual": str(line_sum),
                "delta": str(abs(line_sum - net_of_vat)),
                "severity": "error",
            })

    # --- Check 2: VAT calculation ---
    expected_vat = (net_of_vat * vat_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if abs(expected_vat - vat_amount) > _TOLERANCE:
        findings.append({
            "code": "VAT_AMOUNT_MISMATCH",
            "expected": str(expected_vat),
            "actual": str(vat_amount),
            "delta": str(abs(expected_vat - vat_amount)),
            "severity": "error",
        })

    # --- Check 3: gross total ---
    expected_gross = net_of_vat + vat_amount
    if abs(expected_gross - gross_total) > _TOLERANCE:
        findings.append({
            "code": "GROSS_TOTAL_MISMATCH",
            "expected": str(expected_gross),
            "actual": str(gross_total),
            "delta": str(abs(expected_gross - gross_total)),
            "severity": "error",
        })

    # --- Check 4: withholding ---
    expected_wht = (net_of_vat * withholding_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if abs(expected_wht - withholding_amount) > _TOLERANCE:
        findings.append({
            "code": "WITHHOLDING_MISMATCH",
            "expected": str(expected_wht),
            "actual": str(withholding_amount),
            "delta": str(abs(expected_wht - withholding_amount)),
            "severity": "error",
        })

    # --- Check 5: expected payable ---
    expected_payable = gross_total - withholding_amount

    if abs(expected_payable - printed_total_due) > _TOLERANCE:
        findings.append({
            "code": "PRINTED_TOTAL_DUE_MISMATCH",
            "expected": str(expected_payable),
            "actual": str(printed_total_due),
            "delta": str(abs(expected_payable - printed_total_due)),
            "severity": "error",
        })

    status = "validated" if not findings else "needs_review"
    return {
        "status": status,
        "expected_payable": expected_payable,
        "printed_total_due": printed_total_due,
        "findings": findings,
    }
