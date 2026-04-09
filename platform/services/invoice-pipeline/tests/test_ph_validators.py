"""Tests for PH deterministic invoice validation engine.

Golden fixtures test the core TaxPulse PH gate: does the validator
correctly flag mismatched invoices and pass clean ones?
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.ph_models import (
    FindingSeverity,
    PHInvoice,
    PHLineItem,
    TaxType,
    ValidationStatus,
)
from app.ph_validators import PHValidationEngine

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> PHInvoice:
    """Load a golden fixture JSON into a PHInvoice."""
    with open(FIXTURES_DIR / name) as f:
        data = json.load(f)
    # Remove test-only keys
    data.pop("_test_note", None)
    return PHInvoice(**data)


@pytest.fixture
def engine():
    return PHValidationEngine()


# ---------------------------------------------------------------------------
# Clean invoice — must pass
# ---------------------------------------------------------------------------


class TestCleanVATInvoice:
    def test_validated_status(self, engine):
        invoice = load_fixture("clean_vat_invoice.json")
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.validated

    def test_no_errors(self, engine):
        invoice = load_fixture("clean_vat_invoice.json")
        result = engine.validate(invoice)
        errors = [f for f in result.findings if f.severity == FindingSeverity.error]
        assert len(errors) == 0

    def test_expected_payable(self, engine):
        invoice = load_fixture("clean_vat_invoice.json")
        result = engine.validate(invoice)
        # gross 112000 - withholding 2000 = 110000
        assert result.expected_payable == Decimal("110000.00")
        assert result.delta <= Decimal("1.00")


# ---------------------------------------------------------------------------
# Mismatched payable — must flag needs_review
# ---------------------------------------------------------------------------


class TestMismatchedPayableInvoice:
    def test_needs_review_status(self, engine):
        invoice = load_fixture("mismatched_payable_invoice.json")
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.needs_review

    def test_payable_error_finding(self, engine):
        invoice = load_fixture("mismatched_payable_invoice.json")
        result = engine.validate(invoice)
        payable_findings = [f for f in result.findings if f.rule == "expected_payable"]
        assert len(payable_findings) == 1
        assert payable_findings[0].severity == FindingSeverity.error

    def test_delta_is_nonzero(self, engine):
        invoice = load_fixture("mismatched_payable_invoice.json")
        result = engine.validate(invoice)
        # Expected payable = 35840 - 320 = 35520, printed 36000, delta = 480
        assert result.delta == Decimal("480.00")


# ---------------------------------------------------------------------------
# Zero-rated invoice — must pass (VAT = 0)
# ---------------------------------------------------------------------------


class TestZeroRatedInvoice:
    def test_validated_status(self, engine):
        invoice = load_fixture("zero_rated_invoice.json")
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.validated

    def test_zero_vat(self, engine):
        invoice = load_fixture("zero_rated_invoice.json")
        result = engine.validate(invoice)
        assert result.expected_vat == Decimal("0")

    def test_payable_equals_gross(self, engine):
        invoice = load_fixture("zero_rated_invoice.json")
        result = engine.validate(invoice)
        assert result.expected_payable == Decimal("250000.00")


# ---------------------------------------------------------------------------
# Withholding mismatch — must flag
# ---------------------------------------------------------------------------


class TestWithholdingMismatchInvoice:
    def test_needs_review_status(self, engine):
        invoice = load_fixture("withholding_mismatch_invoice.json")
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.needs_review

    def test_withholding_error(self, engine):
        invoice = load_fixture("withholding_mismatch_invoice.json")
        result = engine.validate(invoice)
        ewt_findings = [f for f in result.findings if f.rule == "withholding_computation"]
        assert len(ewt_findings) == 1
        assert ewt_findings[0].severity == FindingSeverity.error


# ---------------------------------------------------------------------------
# Low confidence — must flag even if math is correct
# ---------------------------------------------------------------------------


class TestLowConfidenceInvoice:
    def test_needs_review_status(self, engine):
        invoice = load_fixture("low_confidence_invoice.json")
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.needs_review

    def test_confidence_error(self, engine):
        invoice = load_fixture("low_confidence_invoice.json")
        result = engine.validate(invoice)
        conf_findings = [f for f in result.findings if f.rule == "extraction_confidence"]
        assert len(conf_findings) == 1
        assert conf_findings[0].severity == FindingSeverity.error


# ---------------------------------------------------------------------------
# Unit tests for decimal helpers
# ---------------------------------------------------------------------------


class TestDecimalHelpers:
    def test_round2_half_up(self):
        from app.ph_models import round2, d
        assert round2(d("100.005")) == Decimal("100.01")
        assert round2(d("100.004")) == Decimal("100.00")
        assert round2(d("0.125")) == Decimal("0.13")

    def test_vat_computation_precision(self):
        """Verify 12% VAT on PHP 100,000 = exactly PHP 12,000."""
        from app.ph_models import round2, d
        base = d("100000.00")
        vat_rate = d("0.12")
        assert round2(base * vat_rate) == Decimal("12000.00")

    def test_ewt_computation_precision(self):
        """Verify 2% EWT on PHP 500,000 = exactly PHP 10,000."""
        from app.ph_models import round2, d
        base = d("500000.00")
        ewt_rate = d("0.02")
        assert round2(base * ewt_rate) == Decimal("10000.00")


# ---------------------------------------------------------------------------
# Programmatic invoice construction
# ---------------------------------------------------------------------------


class TestProgrammaticInvoice:
    def test_multi_line_vatable(self, engine):
        """Multi-line vatable invoice with correct math."""
        invoice = PHInvoice(
            supplier_name="Test Vendor",
            supplier_tin="000-000-000-000",
            invoice_no="TEST-001",
            invoice_date="2026-04-09",
            lines=[
                PHLineItem(
                    line_no=1, description="Service A",
                    quantity=Decimal("1"), unit_price=Decimal("50000"),
                    amount=Decimal("50000"), tax_type=TaxType.vatable,
                    ewt_rate=Decimal("0.02"),
                ),
                PHLineItem(
                    line_no=2, description="Service B",
                    quantity=Decimal("2"), unit_price=Decimal("25000"),
                    amount=Decimal("50000"), tax_type=TaxType.vatable,
                    ewt_rate=Decimal("0.02"),
                ),
            ],
            printed_subtotal=Decimal("100000"),
            printed_vat=Decimal("12000"),
            printed_gross=Decimal("112000"),
            printed_withholding=Decimal("2000"),
            printed_total_due=Decimal("110000"),
            extraction_confidence=0.97,
        )
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.validated
        assert result.expected_payable == Decimal("110000.00")

    def test_vat_exempt_line(self, engine):
        """VAT-exempt line should not contribute to VAT base."""
        invoice = PHInvoice(
            supplier_name="Exempt Vendor",
            supplier_tin="111-111-111-000",
            invoice_no="EX-001",
            invoice_date="2026-04-09",
            lines=[
                PHLineItem(
                    line_no=1, description="Exempt goods",
                    quantity=Decimal("1"), unit_price=Decimal("10000"),
                    amount=Decimal("10000"), tax_type=TaxType.vat_exempt,
                ),
            ],
            printed_subtotal=Decimal("10000"),
            printed_vat=Decimal("0"),
            printed_gross=Decimal("10000"),
            printed_withholding=Decimal("0"),
            printed_total_due=Decimal("10000"),
            extraction_confidence=0.95,
        )
        result = engine.validate(invoice)
        assert result.status == ValidationStatus.validated
        assert result.expected_vat == Decimal("0")
