# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: Helpdesk Refunds",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Use ipai_helpdesk (merge) instead. Do not install.",
    "description": """
Helpdesk Refunds
================

Gift card reimbursements

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for helpdesk refunds
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > Helpdesk Refunds

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["ipai_helpdesk"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": False,
    "application": False,
    "auto_install": False,
}
