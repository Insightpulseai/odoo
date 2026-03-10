from __future__ import annotations
from dataclasses import dataclass
from .schemas import InvoiceExtraction, ExpenseExtraction


@dataclass
class ValidationDecision:
    ok: bool
    confidence: float
    reason: str
    dupe_risk: float = 0.0


def validate_invoice(inv: InvoiceExtraction) -> ValidationDecision:
    if inv.total <= 0:
        return ValidationDecision(False, inv.confidence, "total must be > 0", 0.0)
    # Numeric reconciliation when available
    if inv.subtotal is not None and inv.vat is not None:
        approx = inv.subtotal + inv.vat
        # tolerance 2% or 2 currency units, whichever larger
        tol = max(2.0, 0.02 * max(inv.total, 1.0))
        if abs(approx - inv.total) > tol:
            return ValidationDecision(
                False,
                min(inv.confidence, 0.6),
                "subtotal+vat does not match total within tolerance",
                0.0,
            )
    return ValidationDecision(True, inv.confidence, "ok", 0.0)


def validate_expense(exp: ExpenseExtraction) -> ValidationDecision:
    if exp.amount <= 0:
        return ValidationDecision(False, exp.confidence, "amount must be > 0", 0.0)
    if not exp.description.strip():
        return ValidationDecision(False, min(exp.confidence, 0.6), "description required", 0.0)
    return ValidationDecision(True, exp.confidence, "ok", 0.0)
