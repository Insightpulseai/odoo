# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Google Workspace Add-ons",
    "version": "19.0.1.0.0",
    "summary": "Self-hosted Google Workspace Add-ons (Gmail, Calendar, Drive, Sheets)",
    "description": """
IPAI Google Workspace Add-ons
==============================

HTTP-based Google Workspace Add-ons with Odoo as the backend.
Google sends POST requests with context (email, event, file selection);
Odoo returns Card Service v1 JSON rendered in the Workspace sidebar.

Supported triggers:
  - Gmail: contextual sidebar (sender lookup, recent activity, quick actions)
  - Calendar: event open (attendee info, related records)
  - Drive: items selected (attach to Odoo record, OCR scan)
  - Sheets: file scope (import/export Odoo data)

Architecture:
  Google Workspace → HTTPS POST → Odoo controller → Card JSON response
  Auth: Google-signed ID token verified via google-auth library

Configuration:
  Settings → General Settings → Google Workspace section
  - Enable/disable the add-on
  - Set Google Cloud project number (for token audience validation)

Deployment:
  gcloud workspace-add-ons deployments create ipai-workspace \\
    --deployment-file=config/gws/deployment.json
    """,
    "category": "Tools",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
