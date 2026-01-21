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
            ("mailgun", "Mailgun"),
            ("smtp", "Generic SMTP"),
            ("postfix", "Local Postfix"),
        ],
        string="Mail Provider",
        config_parameter="ipai.mail.provider",
        default="mailgun",
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

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            ipai_mail_provider=params.get_param("ipai.mail.provider", "mailgun"),
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
        params.set_param("ipai.mail.provider", self.ipai_mail_provider or "mailgun")
        params.set_param("ipai.mailgun.api_key", self.ipai_mailgun_api_key or "")
        params.set_param("ipai.mailgun.domain", self.ipai_mailgun_domain or "")
        params.set_param("mail.catchall.domain", self.ipai_mail_catchall_domain or "")
        params.set_param("ipai.oauth.google.enabled", self.ipai_oauth_google_enabled)
        params.set_param("ipai.oauth.azure.enabled", self.ipai_oauth_azure_enabled)
        params.set_param("ipai.iot.enabled", self.ipai_iot_enabled)
        params.set_param("ipai.iot.mqtt.broker", self.ipai_iot_mqtt_broker or "localhost")
        params.set_param("ipai.iot.mqtt.port", self.ipai_iot_mqtt_port or 1883)
