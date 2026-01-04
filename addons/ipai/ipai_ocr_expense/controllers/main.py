# -*- coding: utf-8 -*-
"""
OCR Expense Controllers.

REST API endpoints for OCR integration and webhook handling.
"""
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiOcrExpenseController(http.Controller):
    """
    Controller for OCR Expense API endpoints.

    Provides:
    - Webhook for async OCR completion callbacks
    - API for checking OCR status
    """

    @http.route(
        "/ipai/ocr/webhook",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def ocr_webhook(self, **kwargs):
        """
        Webhook endpoint for OCR provider callbacks.

        Called by external OCR service when async processing completes.
        Updates the corresponding expense record with extracted data.
        """
        try:
            data = request.jsonrequest

            transaction_id = data.get("transaction_id")
            if not transaction_id:
                return {"status": "error", "message": "Missing transaction_id"}

            # Find the expense by OCR token
            expense = (
                request.env["hr.expense"]
                .sudo()
                .search([("ocr_token", "=", transaction_id)], limit=1)
            )

            if not expense:
                return {"status": "error", "message": "Expense not found"}

            # Update with extracted data
            status = data.get("status", "completed")
            if status == "completed":
                expense.write(
                    {
                        "digitization_status": "completed",
                        "ai_total_amount": data.get("amount", 0.0),
                        "ai_vendor_name": data.get("vendor", ""),
                        "ai_expense_date": data.get("date"),
                        "ai_confidence_score": data.get("confidence", 0.0),
                        "ai_raw_text": data.get("raw_text", ""),
                    }
                )
            else:
                expense.write(
                    {
                        "digitization_status": "failed",
                    }
                )

            return {"status": "ok", "expense_id": expense.id}

        except Exception as e:
            _logger.error("OCR webhook error: %s", str(e))
            return {"status": "error", "message": str(e)}

    @http.route(
        "/ipai/ocr/status/<int:expense_id>",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_ocr_status(self, expense_id):
        """
        Get OCR processing status for an expense.

        Args:
            expense_id: ID of the expense record

        Returns:
            dict: OCR status and extracted data
        """
        expense = request.env["hr.expense"].browse(expense_id)
        if not expense.exists():
            return {"status": "error", "message": "Expense not found"}

        return {
            "status": "ok",
            "expense_id": expense.id,
            "digitization_status": expense.digitization_status,
            "ocr_token": expense.ocr_token,
            "ai_data": {
                "amount": expense.ai_total_amount,
                "vendor": expense.ai_vendor_name,
                "date": expense.ai_expense_date.isoformat() if expense.ai_expense_date else None,
                "confidence": expense.ai_confidence_score,
            },
            "needs_review": expense.needs_review,
        }
