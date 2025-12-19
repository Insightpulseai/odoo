# -*- coding: utf-8 -*-
"""
IDP API Controller.

REST API endpoints for document processing.
"""
import base64
import json
import logging

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class IdpApiController(http.Controller):
    """
    IDP REST API Controller.

    Endpoints:
        /ipai/idp/api/extract_preview - Test extraction without saving
        /ipai/idp/api/validate - Validate extraction data
        /ipai/idp/api/documents - Document CRUD
    """

    @http.route("/ipai/idp/api/extract_preview", type="json", auth="user")
    def extract_preview(self, ocr_text, doc_type="invoice"):
        """
        Preview extraction without creating records.

        Useful for testing prompts and schemas.

        Args:
            ocr_text: Raw OCR text
            doc_type: Document type (invoice, receipt, etc.)

        Returns:
            dict: Extraction preview result
        """
        try:
            result = (
                request.env["idp.service.extractor"]
                .sudo()
                .extract_preview(ocr_text, doc_type)
            )
            return result
        except Exception as e:
            _logger.exception("Extract preview failed")
            return {"error": str(e)}

    @http.route("/ipai/idp/api/validate", type="json", auth="user")
    def validate_data(self, data, doc_type="all"):
        """
        Validate extraction data against rules.

        Args:
            data: dict of extracted data
            doc_type: Document type for rule selection

        Returns:
            dict: Validation result
        """
        try:
            result = (
                request.env["idp.service.validator"]
                .sudo()
                .validate_data(data, doc_type)
            )
            return result
        except Exception as e:
            _logger.exception("Validation failed")
            return {"error": str(e)}

    @http.route("/ipai/idp/api/parse/amount", type="json", auth="user")
    def parse_amount(self, text):
        """
        Parse amount from text.

        Args:
            text: Amount string (e.g., "₱1,234.50")

        Returns:
            dict: Parsed amount and currency
        """
        try:
            parser = request.env["idp.service.parser"].sudo()
            amount, currency = parser.parse_amount_with_currency(text)
            return {
                "amount": amount,
                "currency": currency,
                "original": text,
            }
        except Exception as e:
            return {"error": str(e)}

    @http.route("/ipai/idp/api/parse/date", type="json", auth="user")
    def parse_date(self, text):
        """
        Normalize date string.

        Args:
            text: Date string in various formats

        Returns:
            dict: Normalized date in ISO format
        """
        try:
            parser = request.env["idp.service.parser"].sudo()
            normalized = parser.normalize_date(text)
            return {
                "date": normalized,
                "original": text,
            }
        except Exception as e:
            return {"error": str(e)}

    @http.route("/ipai/idp/api/documents", type="json", auth="user", methods=["GET"])
    def list_documents(self, status=None, doc_type=None, limit=50, offset=0):
        """
        List documents with optional filtering.

        Args:
            status: Filter by status
            doc_type: Filter by document type
            limit: Max records to return
            offset: Pagination offset

        Returns:
            dict: List of documents
        """
        try:
            domain = []
            if status:
                domain.append(("status", "=", status))
            if doc_type:
                domain.append(("doc_type", "=", doc_type))

            Document = request.env["idp.document"].sudo()
            total = Document.search_count(domain)
            documents = Document.search(domain, limit=limit, offset=offset)

            result = []
            for doc in documents:
                result.append(
                    {
                        "id": doc.id,
                        "name": doc.name,
                        "status": doc.status,
                        "doc_type": doc.doc_type,
                        "source": doc.source,
                        "create_date": (
                            doc.create_date.isoformat() if doc.create_date else None
                        ),
                    }
                )

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "documents": result,
            }
        except Exception as e:
            _logger.exception("List documents failed")
            return {"error": str(e)}

    @http.route("/ipai/idp/api/documents", type="json", auth="user", methods=["POST"])
    def create_document(self, file_base64=None, filename=None, source="api"):
        """
        Create a new document from uploaded file.

        Args:
            file_base64: Base64 encoded file content
            filename: Original filename
            source: Document source

        Returns:
            dict: Created document info
        """
        try:
            if not file_base64 or not filename:
                return {"error": "file_base64 and filename are required"}

            # Decode file
            file_content = base64.b64decode(file_base64)

            # Create attachment
            attachment = (
                request.env["ir.attachment"]
                .sudo()
                .create(
                    {
                        "name": filename,
                        "datas": file_base64,
                        "type": "binary",
                    }
                )
            )

            # Compute hash
            Document = request.env["idp.document"].sudo()
            file_hash = Document.compute_file_hash(file_content)

            # Check for duplicate
            existing = Document.find_duplicate(file_hash)
            if existing:
                return {
                    "warning": "Duplicate document found",
                    "existing_id": existing.id,
                    "existing_status": existing.status,
                }

            # Create document
            document = Document.create(
                {
                    "attachment_id": attachment.id,
                    "file_hash": file_hash,
                    "source": source,
                    "status": "queued",
                }
            )

            return {
                "id": document.id,
                "name": document.name,
                "status": document.status,
                "message": "Document created and queued for processing",
            }
        except Exception as e:
            _logger.exception("Create document failed")
            return {"error": str(e)}

    @http.route("/ipai/idp/api/documents/<int:document_id>", type="json", auth="user")
    def get_document(self, document_id):
        """
        Get document details and extraction results.

        Args:
            document_id: Document ID

        Returns:
            dict: Document details
        """
        try:
            document = request.env["idp.document"].sudo().browse(document_id)
            if not document.exists():
                return {"error": "Document not found"}

            # Get latest extraction
            extraction_data = {}
            if document.latest_extraction_id:
                ext = document.latest_extraction_id
                extraction_data = {
                    "id": ext.id,
                    "confidence": ext.confidence,
                    "validation_status": ext.validation_status,
                    "extracted_data": ext.get_extracted_data(),
                }

            return {
                "id": document.id,
                "name": document.name,
                "status": document.status,
                "doc_type": document.doc_type,
                "source": document.source,
                "error_message": document.error_message,
                "create_date": (
                    document.create_date.isoformat() if document.create_date else None
                ),
                "processed_at": (
                    document.processed_at.isoformat() if document.processed_at else None
                ),
                "extraction": extraction_data,
                "final_data": (
                    json.loads(document.final_data) if document.final_data else {}
                ),
            }
        except Exception as e:
            _logger.exception("Get document failed")
            return {"error": str(e)}

    @http.route(
        "/ipai/idp/api/documents/<int:document_id>/process",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def process_document(self, document_id):
        """
        Trigger document processing.

        Args:
            document_id: Document ID

        Returns:
            dict: Processing result
        """
        try:
            document = request.env["idp.document"].sudo().browse(document_id)
            if not document.exists():
                return {"error": "Document not found"}

            document.action_process()

            return {
                "id": document.id,
                "status": document.status,
                "message": "Processing completed",
            }
        except Exception as e:
            _logger.exception("Process document failed")
            return {"error": str(e)}

    @http.route(
        "/ipai/idp/api/documents/<int:document_id>/approve",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def approve_document(self, document_id):
        """
        Approve a document.

        Args:
            document_id: Document ID

        Returns:
            dict: Result
        """
        try:
            document = request.env["idp.document"].sudo().browse(document_id)
            if not document.exists():
                return {"error": "Document not found"}

            document.action_approve()

            return {
                "id": document.id,
                "status": document.status,
                "message": "Document approved",
            }
        except Exception as e:
            _logger.exception("Approve document failed")
            return {"error": str(e)}

    @http.route("/ipai/idp/api/model_versions", type="json", auth="user")
    def list_model_versions(self, active_only=True):
        """
        List available model versions.

        Args:
            active_only: Only return active versions

        Returns:
            dict: List of model versions
        """
        try:
            domain = []
            if active_only:
                domain.append(("active", "=", True))

            versions = request.env["idp.model.version"].sudo().search(domain)

            result = []
            for v in versions:
                result.append(
                    {
                        "id": v.id,
                        "name": v.name,
                        "version_code": v.version_code,
                        "doc_type": v.doc_type,
                        "llm_model": v.llm_model,
                        "is_default": v.is_default,
                        "usage_count": v.usage_count,
                        "success_rate": v.success_rate,
                        "avg_confidence": v.avg_confidence,
                    }
                )

            return {"versions": result}
        except Exception as e:
            _logger.exception("List model versions failed")
            return {"error": str(e)}
