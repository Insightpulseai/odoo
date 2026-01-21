# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # IoT Bridge Settings
    ipai_iot_enabled = fields.Boolean(
        string="Enable IoT Bridge",
        config_parameter="ipai_iot.enabled",
        help="Enable IoT device integration (replaces EE iot module)",
    )

    ipai_iot_gateway_url = fields.Char(
        string="Default Gateway URL",
        config_parameter="ipai_iot.gateway_url",
        help="URL of self-hosted IoT gateway",
    )

    ipai_iot_cups_server = fields.Char(
        string="CUPS Server",
        config_parameter="ipai_iot.cups_server",
        default="localhost:631",
        help="CUPS print server address",
    )

    ipai_iot_printnode_enabled = fields.Boolean(
        string="Enable PrintNode",
        config_parameter="ipai_iot.printnode_enabled",
        help="Enable PrintNode cloud printing",
    )

    ipai_iot_printnode_api_key = fields.Char(
        string="PrintNode API Key",
        config_parameter="ipai_iot.printnode_api_key",
    )

    ipai_iot_auto_discover = fields.Boolean(
        string="Auto-Discover Devices",
        config_parameter="ipai_iot.auto_discover",
        default=True,
        help="Automatically discover devices on gateway startup",
    )
