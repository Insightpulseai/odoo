# -*- coding: utf-8 -*-
{
    "name": "IPAI IoT Bridge",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/IoT",
    "summary": "IoT device bridge for CE+OCA without EE IoT dependencies",
    "description": """
IPAI IoT Bridge
===============

IoT device integration for IPAI CE+OCA stack without Enterprise IoT dependencies.

Features:
- Direct device communication via MQTT
- REST API device integration
- Device registry and management
- Real-time data collection
- Alert and notification system
- No Enterprise IoT box required

This module replaces Enterprise IoT with direct device integrations.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_enterprise_bridge",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/iot_bridge_data.xml",
        "views/iot_bridge_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
