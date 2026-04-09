"""TaxPulse PH — Deterministic invoice validation engine.

Constitution C2.1: All tax math must be computed in code and reproducible
from fixtures. No AI involvement in correctness decisions.

Standard PH VAT rate: 12%
EWT rates: per BIR RR No. 2-98 as amended (1%, 2%, 5%, 10%, 15%)
"""

from __future__ import annotations

import logging
from decimal import Decimal

from app.ph_models import (
    Finding,
    FindingSeverity,
    PHInvoice,
    PHLineItem,
    PHValidationResult,
    TaxType,
    ValidationStatus,
    d,
    round2,
)

logger = logging.getLogger(__name__)

PH_VAT_RATE = Decimal("0.12")
TOLERANCE = Decimal("1.00")  # PHP 1.00 tolerance for rounding differences


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------


def _check_line_sum(invoice: PHInvoice) -> list[Finding]:
    """Verify that line item amounts sum to the printed subtotal."""
    findings: list[Finding] = []
    if not invoice.lines:
        findings.append(Finding(
            rule="line_items_present",
            severity=FindingSeverity.warning,
            message="No line items found — cannot verify line-level math",
            field="lines",
        ))
        return findings

    computed_subtotal = sum(line.amount for line in invoice.lines)
    diff = abs(computed_subtotal - invoice.printed_subtotal)

    if diff > TOLERANCE:
        findings.append(Finding(
            rule="line_sum_matches_subtotal",
            severity=FindingSeverity.error,
            message=f"Line item sum ({computed_subtotal}) does not match printed subtotal ({invoice.printed_subtotal})",
            expected=str(invoice.printed_subtotal),
            actual=str(computed_subtotal),
            field="printed_subtotal",
        ))
    return findings


def _check_vat(invoice: PHInvoice) -> list[Finding]:
    """Verify VAT computation: 12% of vatable subtotal."""
    findings: list[Finding] = []

    vatable_base = Decimal("0")
    for line in invoice.lines:
        if line.tax_type == TaxType.vatable:
            vatable_base += line.amount

    expected_vat = round2(vatable_base * PH_VAT_RATE)
    diff = abs(expected_vat - invoice.printed_vat)

    if diff > TOLERANCE:
        findings.append(Finding(
            rule="vat_computation",
            severity=FindingSeverity.error,
            message=f"Expected VAT {expected_vat} (12% of {vatable_base}), printed {invoice.printed_vat}",
            expected=str(expected_vat),
            actual=str(invoice.printed_vat),
            field="printed_vat",
        ))

    return findings, expected_vat, vatable_base


def _check_withholding(invoice: PHInvoice) -> list[Finding]:
    """Verify withholding (EWT) computation from line-level rates."""
    findings: list[Finding] = []

    expected_ewt = Decimal("0")
    for line in invoice.lines:
        if line.ewt_rate > 0:
            line_ewt = round2(line.amount * line.ewt_rate)
            expected_ewt += line_ewt

    diff = abs(expected_ewt - invoice.printed_withholding)

    if diff > TOLERANCE:
        findings.append(Finding(
            rule="withholding_computation",
            severity=FindingSeverity.error,
            message=f"Expected withholding {expected_ewt}, printed {invoice.printed_withholding}",
            expected=str(expected_ewt),
            actual=str(invoice.printed_withholding),
            field="printed_withholding",
        ))

    return findings, expected_ewt


def _check_gross(
    invoice: PHInvoice, expected_vat: Decimal
) -> list[Finding]:
    """Verify gross = subtotal + VAT."""
    findings: list[Finding] = []

    expected_gross = round2(invoice.printed_subtotal + expected_vat)
    diff = abs(expected_gross - invoice.printed_gross)

    if diff > TOLERANCE:
        findings.append(Finding(
            rule="gross_total_computation",
            severity=FindingSeverity.error,
            message=f"Expected gross {expected_gross} (subtotal {invoice.printed_subtotal} + VAT {expected_vat}), printed {invoice.printed_gross}",
            expected=str(expected_gross),
            actual=str(invoice.printed_gross),
            field="printed_gross",
        ))

    return findings, expected_gross


def _check_payable(
    invoice: PHInvoice,
    expected_gross: Decimal,
    expected_ewt: Decimal,
) -> list[Finding]:
    """Verify expected payable = gross - withholding, compare to printed total due.

    This is the critical gate: if the printed total due does not match
    the computed payable, the invoice must be flagged for review.
    """
    findings: list[Finding] = []

    expected_payable = round2(expected_gross - expected_ewt)
    diff = abs(expected_payable - invoice.printed_total_due)

    if diff > TOLERANCE:
        findings.append(Finding(
            rule="expected_payable",
            severity=FindingSeverity.error,
            message=f"Expected payable {expected_payable} (gross {expected_gross} - withholding {expected_ewt}), printed total due {invoice.printed_total_due}",
            expected=str(expected_payable),
            actual=str(invoice.printed_total_due),
            field="printed_total_due",
        ))

    return findings, expected_payable, diff


def _check_required_fields(invoice: PHInvoice) -> list[Finding]:
    """Check that critical fields are present."""
    findings: list[Finding] = []

    if not invoice.supplier_name.strip():
        findings.append(Finding(
            rule="supplier_name_present",
            severity=FindingSeverity.error,
            message="Supplier name is missing",
            field="supplier_name",
        ))

    if not invoice.invoice_no.strip():
        findings.append(Finding(
            rule="invoice_no_present",
            severity=FindingSeverity.warning,
            message="Invoice number is missing",
            field="invoice_no",
        ))

    if not invoice.invoice_date.strip():
        findings.append(Finding(
            rule="invoice_date_present",
            severity=FindingSeverity.warning,
            message="Invoice date is missing",
            field="invoice_date",
        ))

    if not invoice.supplier_tin.strip():
        findings.append(Finding(
            rule="supplier_tin_present",
            severity=FindingSeverity.warning,
            message="Supplier TIN is missing — may affect BIR reporting",
            field="supplier_tin",
        ))

    return findings


def _check_confidence(invoice: PHInvoice) -> list[Finding]:
    """Flag low extraction confidence."""
    findings: list[Finding] = []

    if invoice.extraction_confidence < 0.85:
        findings.append(Finding(
            rule="extraction_confidence",
            severity=FindingSeverity.error,
            message=f"Extraction confidence {invoice.extraction_confidence:.2f} is below 0.85 threshold",
            expected=">=0.85",
            actual=f"{invoice.extraction_confidence:.2f}",
            field="extraction_confidence",
        ))
    elif invoice.extraction_confidence < 0.95:
        findings.append(Finding(
            rule="extraction_confidence",
            severity=FindingSeverity.warning,
            message=f"Extraction confidence {invoice.extraction_confidence:.2f} is below 0.95 — manual review recommended",
            expected=">=0.95",
            actual=f"{invoice.extraction_confidence:.2f}",
            field="extraction_confidence",
        ))

    return findings


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class PHValidationEngine:
    """Deterministic PH invoice validation engine.

    Runs all rules against a normalized PHInvoice and returns a
    PHValidationResult with status, computed fields, and findings.
    """

    def validate(self, invoice: PHInvoice) -> PHValidationResult:
        """Execute all PH tax validation rules.

        Returns validated/needs_review/rejected with full findings.
        """
        all_findings: list[Finding] = []

        # Required fields
        all_findings.extend(_check_required_fields(invoice))

        # Confidence
        all_findings.extend(_check_confidence(invoice))

        # Line sum
        all_findings.extend(_check_line_sum(invoice))

        # VAT — returns (findings, expected_vat, vatable_base)
        vat_result = _check_vat(invoice)
        all_findings.extend(vat_result[0])
        expected_vat = vat_result[1]

        # Withholding — returns (findings, expected_ewt)
        ewt_result = _check_withholding(invoice)
        all_findings.extend(ewt_result[0])
        expected_ewt = ewt_result[1]

        # Gross — returns (findings, expected_gross)
        gross_result = _check_gross(invoice, expected_vat)
        all_findings.extend(gross_result[0])
        expected_gross = gross_result[1]

        # Payable — returns (findings, expected_payable, delta)
        payable_result = _check_payable(invoice, expected_gross, expected_ewt)
        all_findings.extend(payable_result[0])
        expected_payable = payable_result[1]
        delta = payable_result[2]

        # Computed subtotal
        expected_subtotal = sum(line.amount for line in invoice.lines) if invoice.lines else invoice.printed_subtotal

        # Determine status
        errors = [f for f in all_findings if f.severity == FindingSeverity.error]
        if errors:
            status = ValidationStatus.needs_review
        else:
            status = ValidationStatus.validated

        # Build explanation summary
        if status == ValidationStatus.validated:
            explanation = "All checks passed. Invoice math is consistent with PH tax rules."
        else:
            error_rules = [f.rule for f in errors]
            explanation = f"Flagged for review: {', '.join(error_rules)}. See findings for details."

        result = PHValidationResult(
            status=status,
            expected_subtotal=round2(d(expected_subtotal)),
            expected_vat=expected_vat,
            expected_gross=expected_gross,
            expected_withholding=expected_ewt,
            expected_payable=expected_payable,
            printed_total_due=invoice.printed_total_due,
            delta=delta,
            findings=all_findings,
            explanation_summary=explanation,
        )

        logger.info(
            "PH validation for %s: %s (findings=%d, errors=%d)",
            invoice.invoice_no or "(no number)",
            status.value,
            len(all_findings),
            len(errors),
        )

        return result
