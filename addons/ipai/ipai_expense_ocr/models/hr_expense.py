# -*- coding: utf-8 -*-
import base64
import json
import logging
import requests
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    # OCR result storage
    ocr_raw_response = fields.Text(
        string="OCR Raw Response",
        help="Raw JSON response from OCR service for audit purposes"
    )
    ocr_extracted_at = fields.Datetime(
        string="OCR Extracted At",
        help="Timestamp when OCR extraction was performed"
    )
    ocr_confidence = fields.Float(
        string="OCR Confidence",
        help="Confidence score from OCR extraction (0-1)"
    )
    ocr_vendor_name = fields.Char(
        string="OCR Vendor",
        help="Vendor name extracted by OCR (before mapping to partner)"
    )

    def action_extract_from_receipt(self):
        """Manual trigger for OCR extraction from attached receipt."""
        self.ensure_one()
        if not self.message_main_attachment_id:
            raise UserError(_("Please attach a receipt image first."))

        self._extract_from_attachment(self.message_main_attachment_id)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("OCR Extraction"),
                "message": _("Receipt data extracted successfully."),
                "type": "success",
                "sticky": False,
            }
        }

    def _extract_from_attachment(self, attachment):
        """Extract expense data from attachment using OCR service."""
        ICP = self.env["ir.config_parameter"].sudo()

        # Get OCR configuration
        ocr_endpoint = ICP.get_param("ipai_expense_ocr.endpoint_url", "")
        ocr_provider = ICP.get_param("ipai_expense_ocr.provider", "custom")
        openai_key = ICP.get_param("ipai_expense_ocr.openai_api_key", "")
        gemini_key = ICP.get_param("ipai_expense_ocr.gemini_api_key", "")

        if not ocr_endpoint and not openai_key and not gemini_key:
            _logger.warning("No OCR service configured. Skipping extraction.")
            return

        # Get attachment data
        file_data = base64.b64decode(attachment.datas)
        file_name = attachment.name
        mime_type = attachment.mimetype or "application/octet-stream"

        try:
            if ocr_provider == "custom" and ocr_endpoint:
                result = self._call_custom_ocr(ocr_endpoint, file_data, file_name, mime_type)
            elif ocr_provider == "openai" and openai_key:
                result = self._call_openai_vision(openai_key, file_data, file_name, mime_type)
            elif ocr_provider == "gemini" and gemini_key:
                result = self._call_gemini_vision(gemini_key, file_data, file_name, mime_type)
            else:
                _logger.warning("No valid OCR provider configured.")
                return

            if result:
                self._apply_ocr_result(result)

        except Exception as e:
            _logger.error("OCR extraction failed: %s", str(e))
            self.ocr_raw_response = json.dumps({"error": str(e)})
            self.ocr_extracted_at = fields.Datetime.now()

    def _call_custom_ocr(self, endpoint_url, file_data, file_name, mime_type):
        """Call custom OCR endpoint (e.g., PaddleOCR-VL service)."""
        _logger.info("Calling custom OCR endpoint: %s", endpoint_url)

        files = {
            "file": (file_name, file_data, mime_type)
        }
        headers = {
            "Accept": "application/json"
        }

        # Add API key if configured
        ICP = self.env["ir.config_parameter"].sudo()
        api_key = ICP.get_param("ipai_expense_ocr.custom_api_key", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            endpoint_url,
            files=files,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()

        return response.json()

    def _call_openai_vision(self, api_key, file_data, file_name, mime_type):
        """Call OpenAI GPT-4 Vision for receipt extraction."""
        _logger.info("Calling OpenAI Vision API")

        # Convert to base64 data URL
        b64_data = base64.b64encode(file_data).decode("utf-8")
        image_url = f"data:{mime_type};base64,{b64_data}"

        prompt = """Analyze this receipt image and extract the following information as JSON:
{
    "vendor_name": "store/vendor name",
    "date": "YYYY-MM-DD format",
    "total": decimal number (main total amount),
    "subtotal": decimal number (before tax if visible),
    "tax": decimal number (tax amount if visible),
    "currency": "3-letter code like PHP, USD",
    "items": [
        {"description": "item name", "quantity": 1, "unit_price": 0.00, "amount": 0.00}
    ],
    "confidence": 0.0 to 1.0 confidence score
}
Return ONLY valid JSON, no markdown or explanation."""

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "max_tokens": 1000
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Parse JSON from response
        # Handle potential markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    def _call_gemini_vision(self, api_key, file_data, file_name, mime_type):
        """Call Google Gemini Vision for receipt extraction."""
        _logger.info("Calling Gemini Vision API")

        b64_data = base64.b64encode(file_data).decode("utf-8")

        prompt = """Analyze this receipt image and extract the following information as JSON:
{
    "vendor_name": "store/vendor name",
    "date": "YYYY-MM-DD format",
    "total": decimal number (main total amount),
    "subtotal": decimal number (before tax if visible),
    "tax": decimal number (tax amount if visible),
    "currency": "3-letter code like PHP, USD",
    "items": [
        {"description": "item name", "quantity": 1, "unit_price": 0.00, "amount": 0.00}
    ],
    "confidence": 0.0 to 1.0 confidence score
}
Return ONLY valid JSON, no markdown or explanation."""

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": b64_data
                            }
                        }
                    ]
                }]
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]

        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    def _apply_ocr_result(self, result):
        """Apply OCR extraction result to expense fields."""
        vals = {
            "ocr_raw_response": json.dumps(result, indent=2),
            "ocr_extracted_at": fields.Datetime.now(),
        }

        # Extract vendor name
        vendor_name = result.get("vendor_name", "")
        if vendor_name:
            vals["ocr_vendor_name"] = vendor_name
            # Try to find matching partner
            partner = self.env["res.partner"].search([
                "|",
                ("name", "ilike", vendor_name),
                ("display_name", "ilike", vendor_name)
            ], limit=1)
            # Note: hr.expense doesn't have partner_id by default
            # You may need to extend the model or use a custom field

        # Extract date
        date_str = result.get("date", "")
        if date_str:
            try:
                # Try common date formats
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        parsed = datetime.strptime(date_str, fmt).date()
                        vals["date"] = parsed
                        break
                    except ValueError:
                        continue
            except Exception as e:
                _logger.warning("Failed to parse date '%s': %s", date_str, e)

        # Extract total
        total = result.get("total")
        if total is not None:
            try:
                vals["total_amount_currency"] = float(total)
            except (ValueError, TypeError):
                pass

        # Extract confidence
        confidence = result.get("confidence")
        if confidence is not None:
            try:
                vals["ocr_confidence"] = float(confidence)
            except (ValueError, TypeError):
                pass

        # Update description with vendor if not set
        if not self.name and vendor_name:
            vals["name"] = vendor_name

        self.write(vals)
        _logger.info("Applied OCR result to expense %s", self.id)


class IrAttachment(models.Model):
    """Hook into attachment creation to trigger OCR on expense attachments."""
    _inherit = "ir.attachment"

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super().create(vals_list)

        # Check if OCR auto-extract is enabled
        ICP = self.env["ir.config_parameter"].sudo()
        auto_extract = ICP.get_param("ipai_expense_ocr.auto_extract", "True")

        if auto_extract.lower() != "true":
            return attachments

        for attachment in attachments:
            # Only process if attached to hr.expense
            if attachment.res_model != "hr.expense" or not attachment.res_id:
                continue

            # Only process image/PDF files
            mime = attachment.mimetype or ""
            if not (mime.startswith("image/") or mime == "application/pdf"):
                continue

            # Trigger OCR extraction
            try:
                expense = self.env["hr.expense"].browse(attachment.res_id)
                if expense.exists():
                    expense._extract_from_attachment(attachment)
            except Exception as e:
                _logger.error("Auto-OCR failed for expense %s: %s", attachment.res_id, e)

        return attachments
