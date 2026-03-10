# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiOcrProvider(models.Model):
    """OCR Provider configuration for external OCR services."""

    _name = "ipai.ocr.provider"
    _description = "OCR Provider"
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    provider_type = fields.Selection(
        [
            ("tesseract", "Tesseract (Local)"),
            ("google_vision", "Google Cloud Vision"),
            ("azure_vision", "Azure Computer Vision"),
            ("aws_textract", "AWS Textract"),
            ("custom", "Custom HTTP API"),
        ],
        string="Provider Type",
        required=True,
        default="tesseract",
    )

    base_url = fields.Char(
        string="API Base URL",
        help="Base URL for HTTP-based providers (e.g., https://vision.googleapis.com/v1)",
    )

    auth_type = fields.Selection(
        [
            ("none", "No Authentication"),
            ("api_key", "API Key"),
            ("bearer", "Bearer Token"),
            ("basic", "Basic Auth"),
        ],
        string="Auth Type",
        default="none",
    )

    # Secrets stored via system params, referenced here by key
    auth_param_key = fields.Char(
        string="Auth Parameter Key",
        help="System parameter key containing the auth token (e.g., ipai.ocr.google_api_key)",
    )

    timeout = fields.Integer(
        string="Timeout (seconds)",
        default=60,
        help="Request timeout for HTTP-based providers",
    )

    max_retries = fields.Integer(
        string="Max Retries", default=3, help="Maximum retry attempts on failure"
    )

    supported_formats = fields.Char(
        string="Supported Formats",
        default="pdf,png,jpg,jpeg,tiff,bmp",
        help="Comma-separated list of supported file extensions",
    )

    notes = fields.Text(string="Notes")

    job_ids = fields.One2many("ipai.ocr.job", "provider_id", string="OCR Jobs")
    job_count = fields.Integer(compute="_compute_job_count")

    @api.depends("job_ids")
    def _compute_job_count(self):
        for rec in self:
            rec.job_count = len(rec.job_ids)

    def get_auth_token(self):
        """Retrieve auth token from system parameters."""
        self.ensure_one()
        if self.auth_param_key:
            return (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(self.auth_param_key, default="")
            )
        return ""

    def test_connection(self):
        """Test provider connection (override per provider type)."""
        self.ensure_one()
        _logger.info("Testing OCR provider: %s (%s)", self.name, self.provider_type)
        # Placeholder - implement per provider
        return {
            "success": True,
            "message": "Connection test not implemented for this provider",
        }
