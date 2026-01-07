import json
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ExpenseOcrResult(models.Model):
    """OCR extraction result for expense receipts."""

    _name = "ipai.expense.ocr.result"
    _description = "Expense OCR Result"
    _order = "create_date desc"

    expense_id = fields.Many2one(
        "hr.expense",
        string="Expense",
        required=True,
        ondelete="cascade",
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Receipt Attachment",
        required=True,
        ondelete="cascade",
    )
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("processing", "Processing"),
            ("extracted", "Extracted"),
            ("needs_review", "Needs Review"),
            ("applied", "Applied"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="queued",
        required=True,
    )

    # Extracted fields
    merchant_name = fields.Char(string="Merchant Name")
    merchant_confidence = fields.Float(string="Merchant Confidence")

    receipt_date = fields.Date(string="Receipt Date")
    date_confidence = fields.Float(string="Date Confidence")

    total_amount = fields.Float(string="Total Amount")
    amount_confidence = fields.Float(string="Amount Confidence")

    currency_code = fields.Char(string="Currency")
    currency_confidence = fields.Float(string="Currency Confidence")

    tax_amount = fields.Float(string="Tax Amount")
    tax_confidence = fields.Float(string="Tax Confidence")

    payment_method = fields.Char(string="Payment Method")
    payment_confidence = fields.Float(string="Payment Method Confidence")

    # Raw data
    extracted_text = fields.Text(string="Extracted Text")
    extraction_json = fields.Text(string="Raw Extraction Data")
    confidence = fields.Float(string="Overall Confidence")

    # Processing metadata
    processing_duration = fields.Float(string="Processing Duration (s)")
    ocr_job_id = fields.Char(string="OCR Job ID")
    error_message = fields.Text(string="Error Message")

    @api.model
    def _get_ocr_service(self):
        """Get the OCR service instance."""
        return self.env["ipai.ocr.service"]

    def action_extract(self):
        """Send receipt to OCR service for extraction."""
        self.ensure_one()

        if not self.attachment_id:
            raise UserError(_("No attachment found."))

        self.state = "processing"
        self.error_message = False

        ocr_service = self._get_ocr_service()

        try:
            start_time = datetime.now()

            # Call OCR service with receipt-specific options
            result = ocr_service.extract_document(
                self.attachment_id.datas,
                self.attachment_id.name,
                options={"doc_type_hint": "receipt"},
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse and store results
            self._parse_ocr_result(result)
            self.processing_duration = duration
            self.extraction_json = json.dumps(result)

            # Determine state based on confidence
            threshold = float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("ipai_expense_ocr.review_threshold", "0.70")
            )

            if self.confidence >= threshold:
                self.state = "extracted"
            else:
                self.state = "needs_review"

            _logger.info(
                f"OCR extraction completed for expense {self.expense_id.id}, "
                f"confidence={self.confidence:.2f}"
            )

        except Exception as e:
            _logger.error(f"OCR extraction failed for expense {self.expense_id.id}: {e}")
            self.state = "failed"
            self.error_message = str(e)

    def _parse_ocr_result(self, result):
        """Parse OCR result and populate fields."""
        fields_data = result.get("fields", {})

        # Merchant
        merchant = fields_data.get("merchant_name", {}) or fields_data.get("vendor_name", {})
        if isinstance(merchant, dict):
            self.merchant_name = merchant.get("value")
            self.merchant_confidence = merchant.get("conf", 0.0)

        # Date
        date_field = fields_data.get("receipt_date", {}) or fields_data.get("invoice_date", {})
        if isinstance(date_field, dict) and date_field.get("value"):
            try:
                self.receipt_date = fields.Date.from_string(date_field["value"])
                self.date_confidence = date_field.get("conf", 0.0)
            except (ValueError, TypeError):
                pass

        # Total amount
        total = fields_data.get("total", {})
        if isinstance(total, dict):
            self.total_amount = total.get("value", 0.0)
            self.amount_confidence = total.get("conf", 0.0)

        # Currency
        currency = fields_data.get("currency", {})
        if isinstance(currency, dict):
            self.currency_code = currency.get("value")
            self.currency_confidence = currency.get("conf", 0.0)

        # Tax
        tax = fields_data.get("tax", {})
        if isinstance(tax, dict):
            self.tax_amount = tax.get("value", 0.0)
            self.tax_confidence = tax.get("conf", 0.0)

        # Payment method
        payment = fields_data.get("payment_method", {})
        if isinstance(payment, dict):
            self.payment_method = payment.get("value")
            self.payment_confidence = payment.get("conf", 0.0)

        # Extracted text
        self.extracted_text = result.get("text", "")

        # Compute overall confidence
        self.confidence = self._compute_overall_confidence(fields_data)

    def _compute_overall_confidence(self, fields_data):
        """Compute average confidence from all extracted fields."""
        confidences = []
        for field in fields_data.values():
            if isinstance(field, dict) and "conf" in field:
                confidences.append(field["conf"])

        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)

    def action_retry(self):
        """Retry failed extraction."""
        self.ensure_one()
        if self.state != "failed":
            raise UserError(_("Only failed extractions can be retried."))

        self.state = "queued"
        self.error_message = False
        return self.action_extract()

    def action_apply(self):
        """Apply extracted fields to the expense."""
        self.ensure_one()
        return self.expense_id.action_apply_ocr_fields()
