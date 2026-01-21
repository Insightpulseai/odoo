# -*- coding: utf-8 -*-
{
    "name": "IPAI IoT Bridge",
    "summary": "IoT device integration for CE (EE iot module replacement)",
    "description": """
IPAI IoT Bridge
===============

This module provides IoT device integration for Odoo CE
without requiring Odoo Enterprise iot modules.

Features:
- Device management (printers, scales, scanners, displays)
- Network and CUPS printer integration
- ESC/POS receipt printer support
- Barcode scanner support
- Integration with PrintNode cloud printing
- No EE dependencies

Replaces:
- iot (EE)
- pos_iot (EE)
- hw_* (EE IoT drivers)
    """,
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Hardware",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        # CE core only - NO EE dependencies
        "base",
        "web",
        # OCA printing (optional)
        # "base_report_to_printer",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/iot_device_views.xml",
        "views/iot_gateway_views.xml",
        "views/res_config_settings_views.xml",
        "data/config_parameters.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
