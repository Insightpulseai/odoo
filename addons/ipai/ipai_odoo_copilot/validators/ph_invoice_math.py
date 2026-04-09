# -*- coding: utf-8 -*-
"""Deterministic PH invoice math validator.

Principle: LLM extracts/explains, deterministic code validates,
Odoo decides workflow state.

This module has ZERO Odoo dependencies so it can be tested offline.
All monetary arithmetic uses ``decimal.Decimal`` to avoid float drift.

Invoice document schema (plain dict)::

    {
        "lines": [
            {"description": str, "qty": number, "unit_cost": number, "amount": number},
            ...
        ],
        "net_of_vat": number,
        "vat_rate": number,          # default 0.12
        "vat_amount": number,
        "gross_total": number,
        "withholding_rate": number,  # default 0.02 (2% EWT)
        "withholding_amount": number,
        "printed_total_due": number,
    }

Returns::

    {
        "status": "validated" | "needs_review",
        "expected_payable": Decimal (as str in JSON),
        "printed_total_due": Decimal (as str in JSON),
        "findings": [
            {
                "code": str,
                "expected": str,
                "actual": str,
                "delta": str,
                "severity": "error" | "warning",
            },
            ...
        ],
    }
"""

from decimal import Decimal, ROUND_HALF_UP

# Rounding tolerance for centavo-level differences
_TOLERANCE = Decimal("0.01")

# Default Philippine tax rates
_DEFAULT_VAT_RATE = Decimal("0.12")
_DEFAULT_EWT_RATE = Decimal("0.02")


def _d(value):
    """Convert a number to Decimal, rounding to 2 decimal places."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _close_enough(a, b):
    """Return True if two Decimal values are within tolerance."""
    return abs(a - b) <= _TOLERANCE


def validate(doc):
    """Validate PH invoice math deterministically.

    Args:
        doc: dict matching the invoice document schema above.

    Returns:
        dict with status, expected_payable, printed_total_due, and findings.
    """
    findings = []

    net_of_vat = _d(doc["net_of_vat"])
    vat_rate = _d(doc.get("vat_rate", _DEFAULT_VAT_RATE))
    vat_amount = _d(doc["vat_amount"])
    gross_total = _d(doc["gross_total"])
    withholding_rate = _d(doc.get("withholding_rate", _DEFAULT_EWT_RATE))
    withholding_amount = _d(doc["withholding_amount"])
    printed_total_due = _d(doc["printed_total_due"])

    # ------------------------------------------------------------------
    # Check 1: LINE_SUM_MISMATCH
    # ------------------------------------------------------------------
    lines = doc.get("lines", [])
    if lines:
        computed_line_sum = sum(
            _d(line["qty"]) * _d(line["unit_cost"]) for line in lines
        )
        computed_line_sum = _d(computed_line_sum)
        reported_line_sum = sum(_d(line["amount"]) for line in lines)
        reported_line_sum = _d(reported_line_sum)

        if not _close_enough(computed_line_sum, reported_line_sum):
            findings.append({
                "code": "LINE_SUM_MISMATCH",
                "expected": str(computed_line_sum),
                "actual": str(reported_line_sum),
                "delta": str(computed_line_sum - reported_line_sum),
                "severity": "error",
            })

    # ------------------------------------------------------------------
    # Check 2: VAT_MISMATCH
    # ------------------------------------------------------------------
    expected_vat = _d(net_of_vat * vat_rate)
    if not _close_enough(expected_vat, vat_amount):
        findings.append({
            "code": "VAT_MISMATCH",
            "expected": str(expected_vat),
            "actual": str(vat_amount),
            "delta": str(expected_vat - vat_amount),
            "severity": "error",
        })

    # ------------------------------------------------------------------
    # Check 3: GROSS_TOTAL_MISMATCH
    # ------------------------------------------------------------------
    expected_gross = _d(net_of_vat + vat_amount)
    if not _close_enough(expected_gross, gross_total):
        findings.append({
            "code": "GROSS_TOTAL_MISMATCH",
            "expected": str(expected_gross),
            "actual": str(gross_total),
            "delta": str(expected_gross - gross_total),
            "severity": "error",
        })

    # ------------------------------------------------------------------
    # Check 4: WITHHOLDING_MISMATCH
    # ------------------------------------------------------------------
    expected_withholding = _d(net_of_vat * withholding_rate)
    if not _close_enough(expected_withholding, withholding_amount):
        findings.append({
            "code": "WITHHOLDING_MISMATCH",
            "expected": str(expected_withholding),
            "actual": str(withholding_amount),
            "delta": str(expected_withholding - withholding_amount),
            "severity": "error",
        })

    # ------------------------------------------------------------------
    # Check 5: PRINTED_TOTAL_DUE_MISMATCH
    # ------------------------------------------------------------------
    expected_payable = _d(gross_total - withholding_amount)
    if not _close_enough(expected_payable, printed_total_due):
        findings.append({
            "code": "PRINTED_TOTAL_DUE_MISMATCH",
            "expected": str(expected_payable),
            "actual": str(printed_total_due),
            "delta": str(expected_payable - printed_total_due),
            "severity": "error",
        })

    status = "validated" if not findings else "needs_review"

    return {
        "status": status,
        "expected_payable": str(expected_payable),
        "printed_total_due": str(printed_total_due),
        "findings": findings,
    }
