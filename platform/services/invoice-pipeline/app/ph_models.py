"""TaxPulse PH — Normalized invoice schema and validation response models.

All monetary fields use Decimal for precision. Philippine tax fields
(VAT, EWT, withholding) are first-class citizens, not afterthoughts.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Decimal helpers — constitution C4.3: decimal-safe with explicit rounding
# ---------------------------------------------------------------------------

TWO_PLACES = Decimal("0.01")


def d(value: float | str | Decimal | None) -> Decimal:
    """Coerce to Decimal, default 0."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def round2(value: Decimal) -> Decimal:
    """Round to 2 decimal places (half-up, PH standard)."""
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TaxType(str, Enum):
    vatable = "vatable"
    zero_rated = "zero_rated"
    vat_exempt = "vat_exempt"


class ValidationStatus(str, Enum):
    validated = "validated"
    needs_review = "needs_review"
    rejected = "rejected"


class FindingSeverity(str, Enum):
    error = "error"
    warning = "warning"
    info = "info"


# ---------------------------------------------------------------------------
# Invoice schema
# ---------------------------------------------------------------------------


class PHLineItem(BaseModel):
    """Single invoice line item with PH tax awareness."""

    line_no: int = 0
    description: str = ""
    quantity: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")
    tax_type: TaxType = TaxType.vatable
    vat_amount: Decimal = Decimal("0")
    ewt_rate: Decimal = Decimal("0")
    ewt_amount: Decimal = Decimal("0")

    model_config = {"json_encoders": {Decimal: str}}


class PHInvoice(BaseModel):
    """Normalized PH invoice — the strict schema all extraction outputs must conform to.

    Constitution C4.2: normalized schema first.
    """

    # Identity
    supplier_name: str = ""
    supplier_tin: str = ""
    customer_name: str = ""
    customer_tin: str = ""
    invoice_no: str = ""
    invoice_date: str = ""

    # Line items
    lines: list[PHLineItem] = Field(default_factory=list)

    # Printed totals (as-extracted from document)
    printed_subtotal: Decimal = Decimal("0")
    printed_vat: Decimal = Decimal("0")
    printed_gross: Decimal = Decimal("0")
    printed_withholding: Decimal = Decimal("0")
    printed_total_due: Decimal = Decimal("0")

    # Extraction metadata
    extraction_confidence: float = 0.0
    extraction_notes: list[str] = Field(default_factory=list)
    source_file: str = ""

    model_config = {"json_encoders": {Decimal: str}}


# ---------------------------------------------------------------------------
# Validation response
# ---------------------------------------------------------------------------


class Finding(BaseModel):
    """A single validation finding — traceable to rule and source field."""

    rule: str
    severity: FindingSeverity
    message: str
    expected: str = ""
    actual: str = ""
    field: str = ""

    model_config = {"json_encoders": {Decimal: str}}


class PHValidationResult(BaseModel):
    """Output of the PH tax validator.

    Constitution C2.4: every decision includes machine-readable findings
    and human-readable explanations.
    """

    status: ValidationStatus
    expected_subtotal: Decimal = Decimal("0")
    expected_vat: Decimal = Decimal("0")
    expected_gross: Decimal = Decimal("0")
    expected_withholding: Decimal = Decimal("0")
    expected_payable: Decimal = Decimal("0")
    printed_total_due: Decimal = Decimal("0")
    delta: Decimal = Decimal("0")
    findings: list[Finding] = Field(default_factory=list)
    explanation_summary: str = ""

    model_config = {"json_encoders": {Decimal: str}}


# ---------------------------------------------------------------------------
# API response envelope
# ---------------------------------------------------------------------------


class AnalyzeResponse(BaseModel):
    """Response from POST /v1/invoices/analyze."""

    success: bool = True
    invoice: PHInvoice
    validation: PHValidationResult
    document_id: str = ""

    model_config = {"json_encoders": {Decimal: str}}


def analyze_error(code: str, message: str) -> dict[str, Any]:
    """Build an error response for the analyze endpoint."""
    return {"success": False, "error": {"code": code, "message": message}}
