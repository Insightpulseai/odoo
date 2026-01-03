# -*- coding: utf-8 -*-
import base64
import json
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiOcrJob(models.Model):
    """OCR Job queue for async document processing."""

    _name = "ipai.ocr.job"
    _description = "OCR Job"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.ocr.job") or "OCR-NEW",
        copy=False,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("done", "Completed"),
        ("failed", "Failed"),
    ], string="Status", default="draft", tracking=True)

    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Source Attachment",
        required=True,
        ondelete="cascade",
    )
    attachment_name = fields.Char(related="attachment_id.name", store=True)
    attachment_mimetype = fields.Char(related="attachment_id.mimetype")

    provider_id = fields.Many2one(
        "ipai.ocr.provider",
        string="OCR Provider",
        domain="[('active', '=', True)]",
    )

    # Source context (what model/record triggered OCR)
    res_model = fields.Char(string="Related Model")
    res_id = fields.Integer(string="Related Record ID")

    # OCR Results
    result_text = fields.Text(string="Extracted Text")
    result_json = fields.Text(string="Raw JSON Response")
    confidence_score = fields.Float(string="Confidence Score")

    # Execution tracking
    started_at = fields.Datetime(string="Started At")
    completed_at = fields.Datetime(string="Completed At")
    duration_seconds = fields.Float(
        string="Duration (s)",
        compute="_compute_duration",
        store=True,
    )

    retry_count = fields.Integer(string="Retry Count", default=0)
    error_message = fields.Text(string="Error Message")

    # Output attachment (store extracted text as separate file)
    output_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Output Attachment",
        readonly=True,
    )

    @api.depends("started_at", "completed_at")
    def _compute_duration(self):
        for rec in self:
            if rec.started_at and rec.completed_at:
                delta = rec.completed_at - rec.started_at
                rec.duration_seconds = delta.total_seconds()
            else:
                rec.duration_seconds = 0.0

    def action_queue(self):
        """Queue job for processing."""
        for rec in self.filtered(lambda r: r.state == "draft"):
            if not rec.provider_id:
                rec.provider_id = self.env["ipai.ocr.provider"].search(
                    [("active", "=", True)], limit=1
                )
            if not rec.provider_id:
                raise UserError("No active OCR provider configured.")
            rec.state = "pending"
        return True

    def action_process(self):
        """Process OCR job (called by cron or manually)."""
        for rec in self.filtered(lambda r: r.state in ("pending", "failed")):
            rec._run_ocr()
        return True

    def action_reset(self):
        """Reset failed job to draft."""
        for rec in self.filtered(lambda r: r.state == "failed"):
            rec.write({
                "state": "draft",
                "error_message": False,
                "retry_count": 0,
            })
        return True

    def _run_ocr(self):
        """Execute OCR processing."""
        self.ensure_one()

        self.write({
            "state": "processing",
            "started_at": fields.Datetime.now(),
            "error_message": False,
        })

        try:
            # Get attachment data
            if not self.attachment_id.datas:
                raise UserError("Attachment has no data")

            file_data = base64.b64decode(self.attachment_id.datas)

            # Route to provider-specific handler
            result = self._call_ocr_provider(file_data)

            # Store results
            self.write({
                "state": "done",
                "completed_at": fields.Datetime.now(),
                "result_text": result.get("text", ""),
                "result_json": json.dumps(result.get("raw", {})),
                "confidence_score": result.get("confidence", 0.0),
            })

            # Create output attachment
            if result.get("text"):
                self._create_output_attachment(result["text"])

            _logger.info("OCR job %s completed successfully", self.name)

        except Exception as e:
            _logger.exception("OCR job %s failed: %s", self.name, str(e))
            self.write({
                "state": "failed",
                "completed_at": fields.Datetime.now(),
                "error_message": str(e),
                "retry_count": self.retry_count + 1,
            })

    def _call_ocr_provider(self, file_data):
        """Call the configured OCR provider."""
        self.ensure_one()

        provider = self.provider_id
        if not provider:
            raise UserError("No OCR provider configured")

        provider_type = provider.provider_type

        if provider_type == "tesseract":
            return self._call_tesseract(file_data)
        elif provider_type == "google_vision":
            return self._call_google_vision(file_data)
        elif provider_type == "azure_vision":
            return self._call_azure_vision(file_data)
        elif provider_type == "custom":
            return self._call_custom_api(file_data)
        else:
            raise UserError(f"Unsupported provider type: {provider_type}")

    def _call_tesseract(self, file_data):
        """Local Tesseract OCR (requires pytesseract)."""
        try:
            import pytesseract
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(file_data))
            text = pytesseract.image_to_string(image)

            return {
                "text": text,
                "raw": {"engine": "tesseract"},
                "confidence": 0.9,
            }
        except ImportError:
            raise UserError("pytesseract not installed. Install with: pip install pytesseract")

    def _call_google_vision(self, file_data):
        """Google Cloud Vision API."""
        import requests

        provider = self.provider_id
        api_key = provider.get_auth_token()

        if not api_key:
            raise UserError("Google Vision API key not configured")

        url = f"{provider.base_url or 'https://vision.googleapis.com/v1'}/images:annotate?key={api_key}"

        payload = {
            "requests": [{
                "image": {"content": base64.b64encode(file_data).decode("utf-8")},
                "features": [{"type": "TEXT_DETECTION"}],
            }]
        }

        response = requests.post(url, json=payload, timeout=provider.timeout)
        response.raise_for_status()

        result = response.json()
        annotations = result.get("responses", [{}])[0].get("textAnnotations", [])

        text = annotations[0]["description"] if annotations else ""

        return {
            "text": text,
            "raw": result,
            "confidence": 0.95,
        }

    def _call_azure_vision(self, file_data):
        """Azure Computer Vision API."""
        import requests

        provider = self.provider_id
        api_key = provider.get_auth_token()

        if not api_key:
            raise UserError("Azure Vision API key not configured")

        url = f"{provider.base_url}/vision/v3.2/read/analyze"

        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/octet-stream",
        }

        response = requests.post(url, headers=headers, data=file_data, timeout=provider.timeout)
        response.raise_for_status()

        # Azure uses async read - would need polling
        # Simplified for demo
        return {
            "text": "",
            "raw": {"status": "submitted"},
            "confidence": 0.0,
        }

    def _call_custom_api(self, file_data):
        """Call custom HTTP API."""
        import requests

        provider = self.provider_id

        if not provider.base_url:
            raise UserError("Custom API base URL not configured")

        headers = {}
        auth_token = provider.get_auth_token()

        if provider.auth_type == "api_key":
            headers["X-API-Key"] = auth_token
        elif provider.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {auth_token}"

        response = requests.post(
            provider.base_url,
            headers=headers,
            files={"file": ("document", file_data)},
            timeout=provider.timeout,
        )
        response.raise_for_status()

        result = response.json()

        return {
            "text": result.get("text", ""),
            "raw": result,
            "confidence": result.get("confidence", 0.0),
        }

    def _create_output_attachment(self, text):
        """Create attachment with extracted text."""
        self.ensure_one()

        output_name = f"{self.attachment_name or 'document'}_ocr.txt"

        attachment = self.env["ir.attachment"].create({
            "name": output_name,
            "datas": base64.b64encode(text.encode("utf-8")),
            "res_model": self.res_model or self._name,
            "res_id": self.res_id or self.id,
            "mimetype": "text/plain",
        })

        self.output_attachment_id = attachment

        return attachment

    @api.model
    def _cron_process_pending_jobs(self):
        """Cron job to process pending OCR jobs."""
        pending = self.search([
            ("state", "=", "pending"),
        ], limit=10, order="create_date asc")

        for job in pending:
            try:
                job._run_ocr()
                self.env.cr.commit()
            except Exception as e:
                _logger.exception("Cron OCR job %s failed: %s", job.name, str(e))
                self.env.cr.rollback()

        _logger.info("Cron processed %d OCR jobs", len(pending))
        return True

    @api.model
    def get_health_status(self):
        """Return health status for monitoring."""
        pending_count = self.search_count([("state", "=", "pending")])
        processing_count = self.search_count([("state", "=", "processing")])
        failed_count = self.search_count([("state", "=", "failed")])

        last_completed = self.search([
            ("state", "=", "done"),
        ], limit=1, order="completed_at desc")

        return {
            "status": "healthy" if failed_count < 10 else "degraded",
            "pending_jobs": pending_count,
            "processing_jobs": processing_count,
            "failed_jobs": failed_count,
            "last_completed": last_completed.completed_at.isoformat() if last_completed.completed_at else None,
            "provider_count": self.env["ipai.ocr.provider"].search_count([("active", "=", True)]),
        }
