"""Invoice Intelligence Pipeline — FastAPI application.

Internal API consumed by the MCP server layer. Not exposed directly to ChatGPT.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.audit import AuditService
from app.config import settings
from app.foundry_di_client import FoundryDIClient
from app.models import (
    Document,
    DocumentHeader,
    DocumentSource,
    DocumentStatus,
    ExtractionInfo,
    LineItem,
    VendorMatch,
    tool_error,
    tool_success,
)
from app.odoo_adapter import OdooAdapter
from app.ph_models import AnalyzeResponse, PHInvoice, PHLineItem, analyze_error
from app.ph_validators import PHValidationEngine
from app.state_machine import DocumentStateMachine
from app.store import DocumentStore
from app.validators import ValidationEngine

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Service singletons (initialized at startup)
# ---------------------------------------------------------------------------
store = DocumentStore()
state_machine = DocumentStateMachine()
validator = ValidationEngine()
ph_validator = PHValidationEngine()
di_client: FoundryDIClient | None = None
odoo_adapter: OdooAdapter | None = None
audit_service = AuditService()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN001
    """Initialize services on startup."""
    global di_client, odoo_adapter  # noqa: PLW0603
    di_client = FoundryDIClient()
    odoo_adapter = OdooAdapter()
    logger.info(
        "Invoice pipeline started (dev_mode=%s, odoo_dev_mode=%s)",
        settings.dev_mode,
        settings.odoo_dev_mode,
    )
    yield
    logger.info("Invoice pipeline shutting down")


app = FastAPI(
    title="Invoice Intelligence Pipeline",
    version="0.1.0",
    description="Document state, extraction orchestration, validation, and audit.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models for endpoints
# ---------------------------------------------------------------------------


class CreateDocumentRequest(BaseModel):
    """Payload for creating a new document record."""

    channel: str = ""
    message_id: str = ""
    chat_id: str = ""
    file_name: str = ""
    blob_url: str = ""
    document_type: str = "invoice"


class ApproveRequest(BaseModel):
    """Payload for approving a document."""

    actor: str = "ap_reviewer"
    notes: str = ""


class RejectRequest(BaseModel):
    """Payload for rejecting a document."""

    actor: str = "ap_reviewer"
    reason: str = ""


class ReprocessRequest(BaseModel):
    """Payload for reprocessing a document."""

    model: str = "prebuilt-invoice"
    actor: str = "system"
    notes: str = ""


class RouteToOdooRequest(BaseModel):
    """Payload for routing a document to Odoo."""

    target: str = "bill"  # "bill" or "expense"
    actor: str = "system"


class MatchVendorRequest(BaseModel):
    """Payload for vendor matching."""

    vendor_name: str = ""
    tax_id: str = ""


class DuplicateCheckRequest(BaseModel):
    """Payload for duplicate checking."""

    document_number: str = ""
    vendor_name: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_document_or_error(document_id: str) -> tuple[Document | None, dict | None]:
    """Fetch document from store; return (doc, None) or (None, error_dict)."""
    doc = store.get(document_id)
    if doc is None:
        return None, tool_error(
            code="NOT_FOUND",
            message=f"Document {document_id} not found",
            document_id=document_id,
        )
    return doc, None


def _transition_or_error(
    doc: Document,
    target: DocumentStatus,
    actor: str = "system",
    notes: str = "",
) -> tuple[Document | None, dict | None]:
    """Attempt state transition; return (doc, None) or (None, error_dict)."""
    try:
        doc = state_machine.transition(doc, target, actor=actor, notes=notes)
        store.update(doc)
        audit_service.record(
            document_id=doc.document_id,
            actor=actor,
            action=f"transition:{doc.audit[-1].old_status}->{target.value}",
            old_status=doc.audit[-1].old_status,
            new_status=target.value,
            notes=notes,
        )
        return doc, None
    except ValueError as exc:
        return None, tool_error(
            code="INVALID_TRANSITION",
            message=str(exc),
            document_id=doc.document_id,
            stage=doc.status.value,
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/v1/documents")
async def create_document(req: CreateDocumentRequest) -> dict[str, Any]:
    """Create a new document record in queued status."""
    source = DocumentSource(
        channel=req.channel,
        message_id=req.message_id,
        chat_id=req.chat_id,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
        file_name=req.file_name,
        blob_url=req.blob_url,
    )
    doc = Document(source=source, document_type=req.document_type)

    try:
        doc = store.create(doc)
    except ValueError as exc:
        return tool_error(code="CONFLICT", message=str(exc))

    audit_service.record(
        document_id=doc.document_id,
        actor="system",
        action="created",
        new_status=doc.status.value,
        notes=f"Ingested from {req.channel or 'api'}",
    )

    return tool_success(
        document_id=doc.document_id,
        status=doc.status.value,
    )


@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str) -> dict[str, Any]:
    """Get full document state."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err
    return tool_success(document=doc.model_dump())


@app.post("/api/v1/documents/{document_id}/extract")
async def start_extraction(document_id: str) -> dict[str, Any]:
    """Start document extraction via Azure Document Intelligence."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    # Transition to extracting
    doc, err = _transition_or_error(doc, DocumentStatus.extracting, notes="Extraction started")
    if err:
        return err

    assert doc is not None
    assert di_client is not None

    try:
        result = await di_client.extract(doc.source.blob_url)

        # Apply extraction results
        header = result["header"]
        if isinstance(header, DocumentHeader):
            doc.header = header
        else:
            doc.header = DocumentHeader(**header)

        items = result["line_items"]
        doc.line_items = [
            item if isinstance(item, LineItem) else LineItem(**item) for item in items
        ]

        vendor = result["vendor"]
        if isinstance(vendor, VendorMatch):
            doc.vendor = vendor
        else:
            doc.vendor = VendorMatch(**vendor)

        doc.extraction = ExtractionInfo(
            provider=result.get("provider", ""),
            model=result.get("model", ""),
            job_id=result.get("job_id", ""),
            confidence=result.get("confidence", 0.0),
            raw_result_ref="",
        )

        # Transition to extracted
        doc, err = _transition_or_error(doc, DocumentStatus.extracted, notes="Extraction complete")
        if err:
            return err

        return tool_success(
            document_id=document_id,
            status=doc.status.value,
            confidence=doc.extraction.confidence,
            vendor=doc.vendor.raw_name,
            total=doc.header.total,
            line_count=len(doc.line_items),
        )

    except Exception as exc:
        # Transition to failed
        _transition_or_error(doc, DocumentStatus.failed, notes=f"Extraction error: {exc}")
        return tool_error(
            code="EXTRACTION_FAILED",
            message=str(exc),
            retryable=True,
            document_id=document_id,
            stage="extracting",
        )


@app.get("/api/v1/documents/{document_id}/extraction")
async def get_extraction_status(document_id: str) -> dict[str, Any]:
    """Get extraction status and metadata."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err
    return tool_success(
        document_id=document_id,
        status=doc.status.value,
        extraction=doc.extraction.model_dump(),
    )


@app.get("/api/v1/documents/{document_id}/fields")
async def get_extracted_fields(document_id: str) -> dict[str, Any]:
    """Get extracted header, line items, and vendor fields."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err
    return tool_success(
        document_id=document_id,
        header=doc.header.model_dump(),
        line_items=[item.model_dump() for item in doc.line_items],
        vendor=doc.vendor.model_dump(),
    )


@app.post("/api/v1/documents/{document_id}/validate")
async def validate_document(document_id: str) -> dict[str, Any]:
    """Run business rules validation."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    # Transition to validating
    doc, err = _transition_or_error(doc, DocumentStatus.validating, notes="Validation started")
    if err:
        return err

    assert doc is not None

    # Run validation
    result = validator.validate(doc)
    doc.validation = result
    store.update(doc)

    # Determine next status based on validation result
    if result.recommended_action == "auto_approve":
        doc, err = _transition_or_error(
            doc,
            DocumentStatus.approved,
            notes=f"Auto-approved (confidence={doc.extraction.confidence:.2f}, all rules passed)",
        )
        if err:
            return err
    else:
        doc, err = _transition_or_error(
            doc,
            DocumentStatus.needs_review,
            notes=f"Routed for review: {', '.join(result.rules_failed) if result.rules_failed else 'low confidence'}",
        )
        if err:
            return err

    assert doc is not None

    return tool_success(
        document_id=document_id,
        status=doc.status.value,
        validation=result.model_dump(),
    )


@app.post("/api/v1/documents/{document_id}/approve")
async def approve_document(document_id: str, req: ApproveRequest) -> dict[str, Any]:
    """Manually approve a document."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    doc, err = _transition_or_error(
        doc, DocumentStatus.approved, actor=req.actor, notes=req.notes or "Manual approval"
    )
    if err:
        return err

    assert doc is not None

    return tool_success(
        document_id=document_id,
        status=doc.status.value,
        approved_by=req.actor,
    )


@app.post("/api/v1/documents/{document_id}/reject")
async def reject_document(document_id: str, req: RejectRequest) -> dict[str, Any]:
    """Reject a document."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    doc, err = _transition_or_error(
        doc, DocumentStatus.rejected, actor=req.actor, notes=req.reason or "Rejected"
    )
    if err:
        return err

    assert doc is not None

    return tool_success(
        document_id=document_id,
        status=doc.status.value,
        rejected_by=req.actor,
        reason=req.reason,
    )


@app.post("/api/v1/documents/{document_id}/reprocess")
async def reprocess_document(document_id: str, req: ReprocessRequest) -> dict[str, Any]:
    """Reprocess a document with a different model or after corrections."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    # Transition to reprocessing
    doc, err = _transition_or_error(
        doc,
        DocumentStatus.reprocessing,
        actor=req.actor,
        notes=req.notes or f"Reprocess with model={req.model}",
    )
    if err:
        return err

    assert doc is not None

    # Transition back to extracting (will trigger new extraction on next /extract call)
    doc, err = _transition_or_error(
        doc,
        DocumentStatus.extracting,
        actor=req.actor,
        notes="Re-extraction initiated",
    )
    if err:
        return err

    assert doc is not None
    assert di_client is not None

    try:
        result = await di_client.extract(doc.source.blob_url, model=req.model)

        header = result["header"]
        doc.header = header if isinstance(header, DocumentHeader) else DocumentHeader(**header)

        items = result["line_items"]
        doc.line_items = [
            item if isinstance(item, LineItem) else LineItem(**item) for item in items
        ]

        vendor = result["vendor"]
        doc.vendor = vendor if isinstance(vendor, VendorMatch) else VendorMatch(**vendor)

        doc.extraction = ExtractionInfo(
            provider=result.get("provider", ""),
            model=result.get("model", ""),
            job_id=result.get("job_id", ""),
            confidence=result.get("confidence", 0.0),
            raw_result_ref="",
        )

        doc, err = _transition_or_error(doc, DocumentStatus.extracted, notes="Re-extraction complete")
        if err:
            return err

        return tool_success(
            document_id=document_id,
            status=doc.status.value,
            confidence=doc.extraction.confidence,
            model_used=req.model,
        )

    except Exception as exc:
        _transition_or_error(doc, DocumentStatus.failed, notes=f"Re-extraction error: {exc}")
        return tool_error(
            code="REPROCESS_FAILED",
            message=str(exc),
            retryable=True,
            document_id=document_id,
            stage="reprocessing",
        )


@app.post("/api/v1/documents/{document_id}/route-to-odoo")
async def route_to_odoo(document_id: str, req: RouteToOdooRequest) -> dict[str, Any]:
    """Create an Odoo record (vendor bill or expense) from the approved document."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    # Transition to posting
    doc, err = _transition_or_error(
        doc, DocumentStatus.posting, actor=req.actor, notes=f"Posting as {req.target}"
    )
    if err:
        return err

    assert doc is not None
    assert odoo_adapter is not None

    try:
        if req.target == "expense":
            odoo_result = await odoo_adapter.create_expense(doc)
        else:
            odoo_result = await odoo_adapter.create_draft_bill(doc)

        doc.finance.draft_odoo_payload_ref = str(odoo_result.get("odoo_record_id", ""))

        # Transition to posted
        doc, err = _transition_or_error(
            doc,
            DocumentStatus.posted,
            actor=req.actor,
            notes=f"Posted to Odoo as {odoo_result.get('odoo_record_name', '')}",
        )
        if err:
            return err

        return tool_success(
            document_id=document_id,
            status=doc.status.value,
            odoo_record_id=odoo_result.get("odoo_record_id"),
            odoo_record_name=odoo_result.get("odoo_record_name"),
        )

    except Exception as exc:
        _transition_or_error(doc, DocumentStatus.failed, notes=f"Odoo posting error: {exc}")
        return tool_error(
            code="POSTING_FAILED",
            message=str(exc),
            retryable=True,
            document_id=document_id,
            stage="posting",
        )


@app.get("/api/v1/documents/{document_id}/audit")
async def get_audit_trail(document_id: str) -> dict[str, Any]:
    """Get the audit trail for a document."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    events = audit_service.get_events(document_id)
    return tool_success(
        document_id=document_id,
        events=[e.model_dump() for e in events],
        count=len(events),
    )


@app.get("/api/v1/documents/{document_id}/audit-pack")
async def export_audit_pack(document_id: str) -> dict[str, Any]:
    """Export the full audit pack for compliance."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    pack = audit_service.export_audit_pack(document_id)
    pack["document"] = doc.model_dump()
    return tool_success(audit_pack=pack)


@app.get("/api/v1/queue/low-confidence")
async def low_confidence_queue(
    threshold: float = Query(default=0.95, ge=0.0, le=1.0),
    limit: int = Query(default=25, ge=1, le=100),
) -> dict[str, Any]:
    """List documents with extraction confidence below threshold."""
    docs = store.list_low_confidence(threshold=threshold, limit=limit)
    return tool_success(
        documents=[
            {
                "document_id": d.document_id,
                "status": d.status.value,
                "confidence": d.extraction.confidence,
                "vendor": d.vendor.raw_name,
                "total": d.header.total,
                "updated_at": d.updated_at,
            }
            for d in docs
        ],
        count=len(docs),
        threshold=threshold,
    )


@app.get("/api/v1/queue/failed")
async def failed_queue(
    since: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    """List failed documents."""
    docs = store.list_failed(since=since, limit=limit)
    return tool_success(
        documents=[
            {
                "document_id": d.document_id,
                "status": d.status.value,
                "vendor": d.vendor.raw_name,
                "error": d.audit[-1].notes if d.audit else "",
                "updated_at": d.updated_at,
            }
            for d in docs
        ],
        count=len(docs),
    )


@app.post("/api/v1/documents/{document_id}/duplicate-check")
async def duplicate_check(
    document_id: str, req: DuplicateCheckRequest
) -> dict[str, Any]:
    """Check for duplicate documents."""
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    doc_number = req.document_number or doc.header.document_number
    vendor_name = req.vendor_name or doc.vendor.raw_name

    duplicates = store.search_duplicates(doc_number, vendor_name)
    # Exclude the current document from results
    duplicates = [d for d in duplicates if d.document_id != document_id]

    return tool_success(
        document_id=document_id,
        duplicates=[
            {
                "document_id": d.document_id,
                "document_number": d.header.document_number,
                "vendor": d.vendor.raw_name,
                "total": d.header.total,
                "status": d.status.value,
            }
            for d in duplicates
        ],
        is_duplicate=len(duplicates) > 0,
        count=len(duplicates),
    )


@app.post("/api/v1/documents/{document_id}/match-vendor")
async def match_vendor(
    document_id: str, req: MatchVendorRequest
) -> dict[str, Any]:
    """Match a vendor name against known vendors.

    In v0, returns a mock match. In v1, queries Odoo res.partner.
    """
    doc, err = _get_document_or_error(document_id)
    if err:
        return err

    vendor_name = req.vendor_name or doc.vendor.raw_name
    tax_id = req.tax_id or doc.vendor.tax_id

    # In v0, simulate vendor matching with a confidence score
    # In v1, this queries Odoo res.partner via the adapter
    doc.vendor.raw_name = vendor_name or doc.vendor.raw_name
    if tax_id:
        doc.vendor.tax_id = tax_id

    # Simple heuristic: if we have a tax_id, higher confidence
    if tax_id:
        doc.vendor.match_confidence = 0.95
        doc.vendor.matched_vendor_name = vendor_name
        doc.vendor.matched_vendor_id = f"partner-{abs(hash(vendor_name)) % 10000}"
    else:
        doc.vendor.match_confidence = 0.75
        doc.vendor.matched_vendor_name = vendor_name
        doc.vendor.matched_vendor_id = ""

    store.update(doc)

    audit_service.record(
        document_id=document_id,
        actor="system",
        action="vendor_matched",
        notes=f"Matched '{vendor_name}' with confidence {doc.vendor.match_confidence:.2f}",
    )

    return tool_success(
        document_id=document_id,
        vendor=doc.vendor.model_dump(),
    )


# ---------------------------------------------------------------------------
# TaxPulse PH — Invoice analysis endpoint
# ---------------------------------------------------------------------------


class AnalyzeInvoiceRequest(BaseModel):
    """Payload for PH invoice analysis."""

    invoice: PHInvoice


@app.post("/api/v1/invoices/analyze")
async def analyze_invoice(req: AnalyzeInvoiceRequest) -> dict[str, Any]:
    """Analyze a normalized PH invoice against deterministic tax rules.

    Accepts a pre-extracted, normalized PHInvoice and returns validation
    findings with computed expected values. Does NOT perform OCR — the
    caller is responsible for extraction and normalization first.

    Returns validated/needs_review/rejected with full findings.
    """
    try:
        result = ph_validator.validate(req.invoice)
        response = AnalyzeResponse(
            invoice=req.invoice,
            validation=result,
        )
        return response.model_dump(mode="json")
    except Exception as exc:
        logger.exception("PH invoice analysis failed")
        return analyze_error("ANALYSIS_FAILED", str(exc))


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "invoice-pipeline",
        "version": "0.1.0",
        "dev_mode": settings.dev_mode,
        "odoo_dev_mode": settings.odoo_dev_mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
