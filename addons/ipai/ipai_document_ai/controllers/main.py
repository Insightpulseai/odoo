import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiDocumentAIController(http.Controller):
    """HTTP endpoints for Document AI operations."""

    @http.route("/ipai/document_ai/upload", type="json", auth="user", methods=["POST"])
    def upload_document(self, attachment_id, res_model=None, res_id=None, **kwargs):
        """
        Create a new document record from an attachment and trigger extraction.

        Args:
            attachment_id: ID of the uploaded attachment
            res_model: Optional related model
            res_id: Optional related record ID

        Returns:
            dict: Created document info
        """
        try:
            attachment = request.env["ir.attachment"].browse(int(attachment_id))
            if not attachment.exists():
                return {"success": False, "error": "Attachment not found"}

            # Check access
            if not request.env.user.has_group(
                "ipai_document_ai.group_document_ai_user"
            ):
                return {"success": False, "error": "Access denied"}

            # Create document
            document = request.env["ipai.document"].create(
                {
                    "name": attachment.name,
                    "attachment_id": attachment.id,
                    "res_model": res_model,
                    "res_id": res_id,
                    "state": "draft",
                }
            )

            # Trigger extraction
            document.action_extract()

            return {
                "success": True,
                "document_id": document.id,
                "state": document.state,
                "confidence": document.confidence,
            }

        except Exception as e:
            _logger.error(f"Document upload failed: {e}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/ipai/document_ai/status/<int:document_id>",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_document_status(self, document_id, **kwargs):
        """
        Get document extraction status.

        Args:
            document_id: Document record ID

        Returns:
            dict: Document status info
        """
        try:
            document = request.env["ipai.document"].browse(document_id)
            if not document.exists():
                return {"success": False, "error": "Document not found"}

            return {
                "success": True,
                "document_id": document.id,
                "state": document.state,
                "confidence": document.confidence,
                "error_message": document.error_message,
                "extracted_fields": {
                    "vendor_name": document.vendor_name,
                    "document_number": document.document_number,
                    "document_date": str(document.document_date)
                    if document.document_date
                    else None,
                    "total_amount": document.total_amount,
                    "tax_amount": document.tax_amount,
                    "currency": document.currency_code,
                },
            }

        except Exception as e:
            _logger.error(f"Get document status failed: {e}")
            return {"success": False, "error": str(e)}

    @http.route(
        "/ipai/document_ai/apply/<int:document_id>",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def apply_document(self, document_id, **kwargs):
        """
        Apply extracted fields to the related record.

        Args:
            document_id: Document record ID

        Returns:
            dict: Result status
        """
        try:
            document = request.env["ipai.document"].browse(document_id)
            if not document.exists():
                return {"success": False, "error": "Document not found"}

            document.action_apply_to_record()

            return {
                "success": True,
                "document_id": document.id,
                "state": document.state,
            }

        except Exception as e:
            _logger.error(f"Apply document failed: {e}")
            return {"success": False, "error": str(e)}

    @http.route("/ipai/document_ai/health", type="json", auth="user", methods=["GET"])
    def ocr_health(self, **kwargs):
        """
        Check OCR service health.

        Returns:
            dict: Health status
        """
        try:
            ocr_service = request.env["ipai.ocr.service"]
            health = ocr_service.check_health()
            return {"success": True, "health": health}

        except Exception as e:
            _logger.error(f"OCR health check failed: {e}")
            return {"success": False, "error": str(e)}
