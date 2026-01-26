# -*- coding: utf-8 -*-
{
    "name": "Electronic Sign",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "Document envelopes for signing",
    "description": """
Electronic Sign
===============

Document envelopes for signing

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for electronic sign
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > Electronic Sign

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
