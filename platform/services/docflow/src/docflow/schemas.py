from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List

DocType = Literal["invoice", "expense", "unknown"]


class Classification(BaseModel):
    document_type: DocType
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class InvoiceLine(BaseModel):
    description: str
    quantity: float = Field(default=1.0)
    unit_price: float
    line_total: float


class InvoiceExtraction(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None  # YYYY-MM-DD
    currency: Optional[str] = None  # ISO-4217
    subtotal: Optional[float] = None
    vat: Optional[float] = None
    total: float
    line_items: List[InvoiceLine] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    notes: Optional[str] = None


class ExpenseExtraction(BaseModel):
    description: str
    date: Optional[str] = None  # YYYY-MM-DD
    amount: float
    currency: Optional[str] = None  # ISO-4217
    merchant: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ProcessResult(BaseModel):
    document_id: str
    source_path: str
    ocr_text_sha256: str
    classification: Classification
    invoice: Optional[InvoiceExtraction] = None
    expense: Optional[ExpenseExtraction] = None
    odoo_model: Optional[str] = None
    odoo_id: Optional[int] = None
    status: Literal["auto_drafted", "needs_review", "failed"] = "failed"
    error: Optional[str] = None
