# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ================================
    # OAuth Configuration
    # ================================
    ipai_oauth_google_enabled = fields.Boolean(
        string="Google OAuth Enabled",
        config_parameter="ipai.oauth.google.enabled",
    )
    ipai_oauth_azure_enabled = fields.Boolean(
        string="Azure AD OAuth Enabled",
        config_parameter="ipai.oauth.azure.enabled",
    )

    # ================================
    # Microsoft Foundry / Azure AI
    # ================================
    ipai_foundry_enabled = fields.Boolean(
        string="Foundry Enabled",
        config_parameter="ipai.foundry.enabled",
        default=False,
    )
    ipai_foundry_endpoint = fields.Char(
        string="Foundry Endpoint",
        config_parameter="ipai.foundry.endpoint",
        help="Azure AI Foundry portal URL.",
    )
    ipai_foundry_project_name = fields.Char(
        string="Foundry Project",
        config_parameter="ipai.foundry.project_name",
    )
    ipai_foundry_model_deployment = fields.Char(
        string="Model Deployment",
        config_parameter="ipai.foundry.model_deployment",
    )
    ipai_foundry_auth_mode = fields.Selection(
        selection=[
            ("managed_identity", "Managed Identity"),
            ("api_key", "API Key"),
            ("oauth2", "OAuth2"),
        ],
        string="Foundry Auth Mode",
        config_parameter="ipai.foundry.auth_mode",
        default="managed_identity",
    )
    ipai_foundry_api_version = fields.Char(
        string="Foundry API Version",
        config_parameter="ipai.foundry.api_version",
        default="2025-03-01-preview",
    )
    ipai_foundry_auth_audience = fields.Char(
        string="Auth Audience",
        config_parameter="ipai.foundry.auth_audience",
        default="https://ai.azure.com/.default",
        help="OAuth2 token audience for the Foundry API.",
    )

    # ================================
    # Document Intelligence / OCR
    # ================================
    ipai_doc_ai_enabled = fields.Boolean(
        string="Document Digitization Enabled",
        config_parameter="ipai.doc_ai.enabled",
        default=False,
    )
    ipai_doc_ai_provider = fields.Selection(
        selection=[
            ("azure_di", "Azure Document Intelligence"),
            ("tesseract", "Tesseract OCR"),
            ("custom", "Custom Endpoint"),
        ],
        string="Doc AI Provider",
        config_parameter="ipai.doc_ai.provider",
        default="azure_di",
    )
    ipai_doc_ai_endpoint = fields.Char(
        string="Doc AI Endpoint",
        config_parameter="ipai.doc_ai.endpoint",
    )
    ipai_doc_ai_model = fields.Char(
        string="Doc AI Model",
        config_parameter="ipai.doc_ai.model",
        default="prebuilt-invoice",
    )
