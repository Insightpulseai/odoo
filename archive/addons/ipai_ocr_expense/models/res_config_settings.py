# -*- coding: utf-8 -*-
"""
IPAI OCR Configuration Settings.

Extends Odoo's settings UI to configure InsightPulse OCR integration:
- Enable/disable OCR functionality
- Configure API endpoint URL
- Set API authentication key

Settings are stored in ir.config_parameter for persistence.
"""
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """
    OCR Configuration Settings.

    Extends res.config.settings to provide UI for configuring
    InsightPulse OCR service connection parameters.

    Settings stored:
        ipai_ocr_expense.ipai_ocr_enabled: Boolean
        ipai_ocr_expense.ipai_ocr_api_url: String
        ipai_ocr_expense.ipai_ocr_api_key: String (consider encryption)
    """

    _inherit = "res.config.settings"

    ipai_ocr_enabled = fields.Boolean(string="Enable InsightPulse OCR")
    ipai_ocr_api_url = fields.Char(
        string="InsightPulse OCR API URL",
        help="Base URL for the OCR endpoint, e.g. https://ocr.insightpulseai.com/api/expense/ocr",
    )
    ipai_ocr_api_key = fields.Char(
        string="InsightPulse OCR API Key",
        help="API key sent as X-API-Key header to the OCR service.",
    )

    def set_values(self):
        """
        Persist OCR settings to ir.config_parameter.

        Stores the OCR configuration values when user saves settings.
        API key is stored as plaintext - consider encryption for production.
        """
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("ipai_ocr_expense.ipai_ocr_enabled", self.ipai_ocr_enabled)
        params.set_param(
            "ipai_ocr_expense.ipai_ocr_api_url", self.ipai_ocr_api_url or ""
        )
        # Store key in ir.config_parameter; you can encrypt separately if needed
        params.set_param(
            "ipai_ocr_expense.ipai_ocr_api_key", self.ipai_ocr_api_key or ""
        )

    @api.model
    def get_values(self):
        """
        Load OCR settings from ir.config_parameter.

        Retrieves stored OCR configuration values when settings page loads.

        Returns:
            dict: Settings values including OCR enabled flag, API URL, and key
        """
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            ipai_ocr_enabled=params.get_param(
                "ipai_ocr_expense.ipai_ocr_enabled", "False"
            )
            == "True",
            ipai_ocr_api_url=params.get_param("ipai_ocr_expense.ipai_ocr_api_url", ""),
            ipai_ocr_api_key=params.get_param("ipai_ocr_expense.ipai_ocr_api_key", ""),
        )
        return res
