# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Settings for Ask AI Bridge - external service configuration only."""

    _inherit = "res.config.settings"

    ask_ai_enabled = fields.Boolean(
        string="Enable Ask AI",
        config_parameter="ipai_ask_ai_bridge.enabled",
        default=False,
    )
    ask_ai_endpoint_url = fields.Char(
        string="Ask AI Endpoint URL",
        config_parameter="ipai_ask_ai_bridge.endpoint_url",
        help="URL of the external Ask AI / Copilot service (e.g., https://copilot.example.com/embed)",
    )
    ask_ai_tenant_id = fields.Char(
        string="Tenant ID",
        config_parameter="ipai_ask_ai_bridge.tenant_id",
        help="Tenant identifier for multi-tenant deployments",
    )
