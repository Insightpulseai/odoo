# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # OCR Provider Selection
    expense_ocr_provider = fields.Selection(
        selection=[
            ("custom", "Custom OCR Endpoint"),
            ("openai", "OpenAI GPT-4 Vision"),
            ("gemini", "Google Gemini Vision"),
        ],
        string="OCR Provider",
        default="custom",
        config_parameter="ipai_expense_ocr.provider",
    )

    # Custom OCR Endpoint
    expense_ocr_endpoint_url = fields.Char(
        string="OCR Endpoint URL",
        help="URL of your custom OCR service (e.g., http://ocr-service:8000/ocr/expense)",
        config_parameter="ipai_expense_ocr.endpoint_url",
    )
    expense_ocr_custom_api_key = fields.Char(
        string="Custom OCR API Key",
        help="API key for custom OCR service (optional)",
        config_parameter="ipai_expense_ocr.custom_api_key",
    )

    # OpenAI Configuration
    expense_ocr_openai_api_key = fields.Char(
        string="OpenAI API Key",
        help="Your OpenAI API key for GPT-4 Vision",
        config_parameter="ipai_expense_ocr.openai_api_key",
    )

    # Gemini Configuration
    expense_ocr_gemini_api_key = fields.Char(
        string="Gemini API Key",
        help="Your Google Gemini API key",
        config_parameter="ipai_expense_ocr.gemini_api_key",
    )

    # Auto-extraction toggle
    expense_ocr_auto_extract = fields.Boolean(
        string="Auto-extract on Upload",
        help="Automatically extract data when a receipt is attached to an expense",
        config_parameter="ipai_expense_ocr.auto_extract",
        default=True,
    )
