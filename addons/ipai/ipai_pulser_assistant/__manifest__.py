# -*- coding: utf-8 -*-
{
    "name": "IPAI Pulser Assistant",
    "version": "18.0.1.0.0",
    "summary": "Reverse SAP Joule — Odoo-native AI copilot with tri-modal behavior, domain agent routing, and audited safe action gates",
    "description": "Pulser assistant framework for Odoo 18. Provides intent taxonomy, action classification, domain agent routing, tool bindings, and append-only audit logging for AI-assisted workflows.",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["base", "mail"],
    "data": [
        "security/pulser_security.xml",
        "security/ir.model.access.csv",
        "views/pulser_action_log_views.xml",
        "views/pulser_domain_agent_views.xml",
        "views/pulser_interaction_views.xml",
        "views/pulser_menu.xml",
    ],
    "installable": True,
    "application": False,
}
