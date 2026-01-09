import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ExpenseOcrController(http.Controller):
    """HTTP endpoints for Expense OCR operations."""

    @http.route("/ipai/expense_ocr/scan/<int:expense_id>", type="json", auth="user", methods=["POST"])
    def scan_expense(self, expense_id, **kwargs):
        """Trigger OCR scan for an expense."""
        try:
            expense = request.env["hr.expense"].browse(expense_id)
            if not expense.exists():
                return {"success": False, "error": "Expense not found"}

            expense.action_scan_receipt()

            return {
                "success": True,
                "expense_id": expense.id,
                "ocr_state": expense.ocr_state,
            }

        except Exception as e:
            _logger.error(f"Expense OCR scan failed: {e}")
            return {"success": False, "error": str(e)}

    @http.route("/ipai/expense_ocr/status/<int:expense_id>", type="json", auth="user", methods=["GET"])
    def get_status(self, expense_id, **kwargs):
        """Get OCR status for an expense."""
        try:
            expense = request.env["hr.expense"].browse(expense_id)
            if not expense.exists():
                return {"success": False, "error": "Expense not found"}

            result = expense.ocr_result_id
            if not result:
                return {
                    "success": True,
                    "expense_id": expense.id,
                    "has_ocr": False,
                }

            return {
                "success": True,
                "expense_id": expense.id,
                "has_ocr": True,
                "state": result.state,
                "confidence": result.confidence,
                "fields": {
                    "merchant_name": result.merchant_name,
                    "receipt_date": str(result.receipt_date) if result.receipt_date else None,
                    "total_amount": result.total_amount,
                    "currency": result.currency_code,
                    "tax_amount": result.tax_amount,
                },
            }

        except Exception as e:
            _logger.error(f"Get expense OCR status failed: {e}")
            return {"success": False, "error": str(e)}

    @http.route("/ipai/expense_ocr/apply/<int:expense_id>", type="json", auth="user", methods=["POST"])
    def apply_ocr(self, expense_id, **kwargs):
        """Apply OCR fields to expense."""
        try:
            expense = request.env["hr.expense"].browse(expense_id)
            if not expense.exists():
                return {"success": False, "error": "Expense not found"}

            expense.action_apply_ocr_fields()

            return {
                "success": True,
                "expense_id": expense.id,
                "state": expense.ocr_state,
            }

        except Exception as e:
            _logger.error(f"Apply expense OCR failed: {e}")
            return {"success": False, "error": str(e)}
