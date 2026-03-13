# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import os
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ===================
    # Email Configuration
    # ===================
    ipai_mail_provider = fields.Selection(
        [
            ("zoho", "Zoho Mail"),          # canonical provider (SSOT: ssot/runtime/prod_settings.yaml)
            ("smtp", "Generic SMTP"),
            ("postfix", "Local Postfix"),
            ("mailgun", "Mailgun"),          # deprecated 2026-02 — kept for migration only
        ],
        string="Mail Provider",
        config_parameter="ipai.mail.provider",
        default="zoho",                     # was: mailgun (deprecated)
    )
    ipai_mailgun_api_key = fields.Char(
        string="Mailgun API Key",
        config_parameter="ipai.mailgun.api_key",
    )
    ipai_mailgun_domain = fields.Char(
        string="Mailgun Domain",
        config_parameter="ipai.mailgun.domain",
        default=lambda self: os.getenv("MAILGUN_DOMAIN", ""),
    )
    ipai_mail_catchall_domain = fields.Char(
        string="Catchall Domain",
        config_parameter="mail.catchall.domain",
    )

    # ===================
    # POS Self-Ordering (Enterprise Feature Stub)
    # ===================
    pos_self_ordering_mode = fields.Selection(
        [
            ("nothing", "Disabled"),
            ("mobile", "QR Code (Mobile)"),
            ("kiosk", "Self-Ordering Kiosk"),
        ],
        string="Self-Ordering Mode",
        default="nothing",
        config_parameter="ipai_bridge.pos_self_ordering_mode",
        help="[Enterprise Feature Stub] Enable POS self-ordering. "
        "Install OCA alternative: pos_order_mgmt or use IPAI Scout vertical.",
    )
    pos_self_ordering_service_mode = fields.Selection(
        [
            ("counter", "Order at Counter"),
            ("table", "Order at Table"),
        ],
        string="Self-Ordering Service Mode",
        default="counter",
        config_parameter="ipai_bridge.pos_self_ordering_service_mode",
        help="[Enterprise Feature Stub] Service mode for self-ordering.",
    )
    pos_self_ordering_pay_after = fields.Selection(
        [
            ("each", "After Each Order"),
            ("meal", "After Meal"),
        ],
        string="Self-Ordering Payment",
        default="each",
        config_parameter="ipai_bridge.pos_self_ordering_pay_after",
        help="[Enterprise Feature Stub] When customers pay in self-ordering flow.",
    )
    pos_self_ordering_image_home_ids = fields.Many2many(
        "ir.attachment",
        "pos_self_ordering_image_home_rel",
        "config_id",
        "image_id",
        string="Self-Ordering Home Images",
        help="[Enterprise Feature Stub] Images displayed on self-ordering home screen.",
    )

    # ===================
    # OAuth Configuration
    # ===================
    ipai_oauth_google_enabled = fields.Boolean(
        string="Google OAuth Enabled",
        config_parameter="ipai.oauth.google.enabled",
    )
    ipai_oauth_azure_enabled = fields.Boolean(
        string="Azure AD OAuth Enabled",
        config_parameter="ipai.oauth.azure.enabled",
    )

    # ===================
    # IoT Configuration
    # ===================
    ipai_iot_enabled = fields.Boolean(
        string="IoT Bridge Enabled",
        config_parameter="ipai.iot.enabled",
    )
    ipai_iot_mqtt_broker = fields.Char(
        string="MQTT Broker Host",
        config_parameter="ipai.iot.mqtt.broker",
        default="localhost",
    )
    ipai_iot_mqtt_port = fields.Integer(
        string="MQTT Broker Port",
        config_parameter="ipai.iot.mqtt.port",
        default=1883,
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
        help="Azure AI Foundry endpoint URL (no secrets).",
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
        default="2024-12-01-preview",
    )

    # ================================
    # Document Digitization / OCR
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
    ipai_doc_ai_storage_mode = fields.Selection(
        selection=[
            ("attachment", "Odoo Attachment"),
            ("azure_blob", "Azure Blob Storage"),
        ],
        string="Doc AI Storage Mode",
        config_parameter="ipai.doc_ai.storage_mode",
        default="attachment",
    )
    ipai_doc_ai_async_enabled = fields.Boolean(
        string="Async Processing",
        config_parameter="ipai.doc_ai.async_enabled",
        default=True,
    )
    ipai_doc_ai_min_file_size = fields.Integer(
        string="Min File Size (KB)",
        config_parameter="ipai.doc_ai.min_file_size",
        default=0,
        help="Minimum file size in KB to process.",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            ipai_mail_provider=params.get_param("ipai.mail.provider", "zoho"),
            ipai_mailgun_api_key=params.get_param("ipai.mailgun.api_key", ""),
            ipai_mailgun_domain=params.get_param("ipai.mailgun.domain", ""),
            ipai_mail_catchall_domain=params.get_param("mail.catchall.domain", ""),
            ipai_oauth_google_enabled=params.get_param("ipai.oauth.google.enabled", False),
            ipai_oauth_azure_enabled=params.get_param("ipai.oauth.azure.enabled", False),
            ipai_iot_enabled=params.get_param("ipai.iot.enabled", False),
            ipai_iot_mqtt_broker=params.get_param("ipai.iot.mqtt.broker", "localhost"),
            ipai_iot_mqtt_port=int(params.get_param("ipai.iot.mqtt.port", 1883)),
        )
        return res

    def set_values(self):
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("ipai.mail.provider", self.ipai_mail_provider or "zoho")
        params.set_param("ipai.mailgun.api_key", self.ipai_mailgun_api_key or "")
        params.set_param("ipai.mailgun.domain", self.ipai_mailgun_domain or "")
        params.set_param("mail.catchall.domain", self.ipai_mail_catchall_domain or "")
        params.set_param("ipai.oauth.google.enabled", self.ipai_oauth_google_enabled)
        params.set_param("ipai.oauth.azure.enabled", self.ipai_oauth_azure_enabled)
        params.set_param("ipai.iot.enabled", self.ipai_iot_enabled)
        params.set_param("ipai.iot.mqtt.broker", self.ipai_iot_mqtt_broker or "localhost")
        params.set_param("ipai.iot.mqtt.port", self.ipai_iot_mqtt_port or 1883)
