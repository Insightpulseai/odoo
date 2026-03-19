# -*- coding: utf-8 -*-
"""
IDP Configuration Settings.

Extends res.config.settings to provide IDP-specific configuration
via the standard Odoo Settings interface.
"""
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """
    IDP Configuration Settings.

    Provides configuration for:
    - OCR API settings
    - LLM API settings
    - Auto-approval thresholds
    - Processing options
    """

    _inherit = "res.config.settings"

    # OCR Configuration
    idp_ocr_enabled = fields.Boolean(
        string="Enable OCR Processing",
        config_parameter="ipai_idp.ocr_enabled",
        default=True,
    )
    idp_ocr_provider = fields.Selection(
        [
            ("insightpulse", "InsightPulse OCR"),
            ("google_vision", "Google Cloud Vision"),
            ("azure", "Azure Form Recognizer"),
            ("tesseract", "Tesseract (Local)"),
        ],
        string="OCR Provider",
        config_parameter="ipai_idp.ocr_provider",
        default="insightpulse",
    )
    idp_ocr_api_url = fields.Char(
        string="OCR API URL",
        config_parameter="ipai_idp.ocr_api_url",
    )
    idp_ocr_api_key = fields.Char(
        string="OCR API Key",
    )

    # LLM Configuration
    idp_llm_enabled = fields.Boolean(
        string="Enable LLM Extraction",
        config_parameter="ipai_idp.llm_enabled",
        default=True,
    )
    idp_llm_provider = fields.Selection(
        [
            ("anthropic", "Anthropic (Claude)"),
            ("openai", "OpenAI"),
            ("azure_openai", "Azure OpenAI"),
        ],
        string="LLM Provider",
        config_parameter="ipai_idp.llm_provider",
        default="anthropic",
    )
    idp_llm_api_url = fields.Char(
        string="LLM API URL",
        config_parameter="ipai_idp.llm_api_url",
        default="https://api.anthropic.com/v1/messages",
    )
    idp_llm_api_key = fields.Char(
        string="LLM API Key",
    )
    idp_llm_model = fields.Selection(
        [
            ("claude-3-sonnet-20240229", "Claude 3 Sonnet"),
            ("claude-3-opus-20240229", "Claude 3 Opus"),
            ("claude-3-haiku-20240307", "Claude 3 Haiku"),
            ("gpt-4-turbo", "GPT-4 Turbo"),
            ("gpt-4", "GPT-4"),
            ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
        ],
        string="Default LLM Model",
        config_parameter="ipai_idp.llm_model",
        default="claude-3-sonnet-20240229",
    )

    # Auto-approval settings
    idp_auto_approve_enabled = fields.Boolean(
        string="Enable Auto-Approval",
        config_parameter="ipai_idp.auto_approve_enabled",
        default=True,
        help="Automatically approve extractions above confidence threshold",
    )
    idp_auto_approve_confidence = fields.Float(
        string="Auto-Approval Confidence Threshold",
        config_parameter="ipai_idp.auto_approve_confidence",
        default=0.90,
        help="Minimum confidence (0.0-1.0) for auto-approval",
    )

    # Processing options
    idp_async_processing = fields.Boolean(
        string="Async Processing (queue_job)",
        config_parameter="ipai_idp.async_processing",
        default=False,
        help="Process documents asynchronously via queue_job",
    )
    idp_max_retries = fields.Integer(
        string="Max Processing Retries",
        config_parameter="ipai_idp.max_retries",
        default=3,
    )
    idp_processing_timeout = fields.Integer(
        string="Processing Timeout (seconds)",
        config_parameter="ipai_idp.processing_timeout",
        default=120,
    )

    def set_values(self):
        """Save API keys to ir.config_parameter (not via config_parameter attr for security)."""
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()

        # Store API keys securely
        if self.idp_ocr_api_key:
            params.set_param("ipai_idp.ocr_api_key", self.idp_ocr_api_key)
        if self.idp_llm_api_key:
            params.set_param("ipai_idp.llm_api_key", self.idp_llm_api_key)

    @api.model
    def get_values(self):
        """Retrieve API keys from ir.config_parameter."""
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()

        res.update(
            idp_ocr_api_key=params.get_param("ipai_idp.ocr_api_key", ""),
            idp_llm_api_key=params.get_param("ipai_idp.llm_api_key", ""),
        )
        return res
