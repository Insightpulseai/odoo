# -*- coding: utf-8 -*-
"""
HR Expense OCR Extension.

Extends hr.expense with AI-powered receipt digitization fields and methods.
Connects to external OCR gateway for document scanning.
"""
import base64
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    """
    Extended HR Expense with OCR Digitization.

    Adds document digitalization capabilities:
    - Receipt image upload
    - OCR processing status
    - AI-extracted data fields
    - Confidence scoring
    """

    _inherit = "hr.expense"

    # ===============================
    # Document Digitalization Fields
    # ===============================
    receipt_image = fields.Binary(
        string="Receipt Scan",
        attachment=True,
        help="Upload receipt image (PNG, JPG, or PDF)",
    )

    receipt_filename = fields.Char(string="Receipt Filename")

    ocr_token = fields.Char(
        string="OCR Transaction ID",
        readonly=True,
        copy=False,
        help="Unique identifier from OCR gateway for tracking",
    )

    # ===============================
    # AI Extracted Data Fields
    # ===============================
    ai_total_amount = fields.Float(
        string="AI Detected Amount",
        readonly=True,
        digits=(16, 2),
        help="Amount extracted by AI from receipt image",
    )

    ai_vendor_name = fields.Char(
        string="AI Detected Vendor",
        readonly=True,
        help="Vendor/merchant name extracted by AI",
    )

    ai_expense_date = fields.Date(
        string="AI Detected Date",
        readonly=True,
        help="Transaction date extracted by AI from receipt",
    )

    ai_confidence_score = fields.Float(
        string="Confidence Score",
        readonly=True,
        digits=(5, 2),
        help="AI confidence percentage (0-100). Review recommended if below 80%.",
    )

    ai_raw_text = fields.Text(
        string="Extracted Text",
        readonly=True,
        help="Raw text extracted from receipt for reference",
    )

    # ===============================
    # Status Fields
    # ===============================
    digitization_status = fields.Selection(
        [
            ("not_started", "Not Started"),
            ("pending", "Scanning..."),
            ("completed", "Digitized"),
            ("failed", "Manual Entry Required"),
            ("validated", "Validated"),
        ],
        string="Digitization Status",
        default="not_started",
        tracking=True,
        help="Current status of AI receipt processing",
    )

    needs_review = fields.Boolean(
        string="Needs Review",
        compute="_compute_needs_review",
        store=True,
        help="True if AI confidence is below threshold",
    )

    ai_data_applied = fields.Boolean(
        string="AI Data Applied",
        default=False,
        help="Whether AI-extracted data has been applied to expense fields",
    )

    # ===============================
    # Computed Fields
    # ===============================
    @api.depends("ai_confidence_score", "digitization_status")
    def _compute_needs_review(self):
        """Flag expenses with low AI confidence for manual review"""
        confidence_threshold = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ocr_expense.confidence_threshold", "80")
        )
        for expense in self:
            expense.needs_review = (
                expense.digitization_status == "completed"
                and expense.ai_confidence_score < confidence_threshold
            )

    # ===============================
    # OCR Actions
    # ===============================
    def action_scan_receipt(self):
        """
        Initiate OCR scanning of uploaded receipt.

        Validates that a receipt image is uploaded, then calls the
        OCR gateway service to extract expense data.
        """
        self.ensure_one()

        if not self.receipt_image:
            raise UserError("Please upload a receipt image first.")

        # Update status to pending
        self.write({"digitization_status": "pending"})

        # Call OCR gateway service
        ocr_service = self.env["ipai.ocr.gateway.service"]
        try:
            result = ocr_service.process_receipt(self)
            if result.get("success"):
                self.write(
                    {
                        "digitization_status": "completed",
                        "ocr_token": result.get("transaction_id"),
                        "ai_total_amount": result.get("amount", 0.0),
                        "ai_vendor_name": result.get("vendor", ""),
                        "ai_expense_date": result.get("date"),
                        "ai_confidence_score": result.get("confidence", 0.0),
                        "ai_raw_text": result.get("raw_text", ""),
                    }
                )
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "OCR Complete",
                        "message": f"Receipt scanned successfully. Confidence: {result.get('confidence', 0):.1f}%",
                        "type": "success",
                        "sticky": False,
                    },
                }
            else:
                self.write({"digitization_status": "failed"})
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "OCR Failed",
                        "message": result.get("error", "Unknown error occurred"),
                        "type": "warning",
                        "sticky": True,
                    },
                }
        except Exception as e:
            _logger.error("OCR processing failed: %s", str(e))
            self.write({"digitization_status": "failed"})
            raise UserError(f"OCR processing failed: {str(e)}")

    def action_apply_ai_data(self):
        """
        Apply AI-extracted data to expense fields.

        Copies AI-detected values to the actual expense fields
        (amount, vendor, date) for submission.
        """
        self.ensure_one()

        if self.digitization_status != "completed":
            raise UserError("OCR must be completed before applying data.")

        vals = {"ai_data_applied": True}

        # Apply amount if detected
        if self.ai_total_amount:
            vals["total_amount_currency"] = self.ai_total_amount

        # Apply vendor name to description if detected
        if self.ai_vendor_name:
            current_name = self.name or ""
            if self.ai_vendor_name not in current_name:
                vals["name"] = f"{current_name} - {self.ai_vendor_name}".strip(" - ")

        # Apply date if detected
        if self.ai_expense_date:
            vals["date"] = self.ai_expense_date

        self.write(vals)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "AI Data Applied",
                "message": "Extracted data has been applied to expense fields.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_validate_ocr(self):
        """Mark OCR extraction as validated by user"""
        self.ensure_one()
        self.write({"digitization_status": "validated"})

    def action_reset_ocr(self):
        """Reset OCR status for re-scanning"""
        self.write(
            {
                "digitization_status": "not_started",
                "ocr_token": False,
                "ai_total_amount": 0.0,
                "ai_vendor_name": False,
                "ai_expense_date": False,
                "ai_confidence_score": 0.0,
                "ai_raw_text": False,
                "ai_data_applied": False,
            }
        )
