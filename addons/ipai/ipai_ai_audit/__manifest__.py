# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Audit & Governance",
    "version": "18.0.1.0.1",
    "category": "Productivity/AI",
    "summary": "AI usage logging, redaction, and governance controls",
    "description": """
IPAI AI Audit & Governance
==========================

Comprehensive audit trail and governance controls for AI usage
across the IPAI platform.

Features:
---------
* **Request Logging**: Full audit trail of AI requests/responses
* **PII Redaction**: Automatic detection and redaction of sensitive data
* **Retention Policies**: Configurable data retention rules
* **Usage Analytics**: Track who used what AI features and when
* **Governance Rules**: Define what AI can and cannot do

Audit Log Contents:
-------------------
- User who made the request
- Timestamp and duration
- Model/provider used
- Token consumption
- Request hash (for deduplication)
- Response hash (for integrity)
- Redacted content snapshots

Governance Controls:
--------------------
- Model whitelists/blacklists
- Rate limiting per user/group
- Sensitive data handling policies
- Export controls

Compliance:
-----------
Supports compliance requirements for:
- Data privacy regulations
- Financial services requirements
- Internal policy enforcement

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ai_audit",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_ai_provider_pulser",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/audit_log_views.xml",
        "views/governance_views.xml",
        "views/menu_views.xml",
        "data/retention_cron.xml",
        "data/redaction_patterns.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
