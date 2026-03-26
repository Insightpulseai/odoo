# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "IPAI Enterprise Bridge",
    "summary": "Minimal stubs and redirections for EE model references (does not reimplement EE features)",
    "version": "19.0.1.2.0",
    "category": "Technical",
    "author": "InsightPulseAI",
    "website": "https://github.com/jgtolentino/odoo",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "mail",
        "auth_oauth",
        # "fetchmail" removed — merged into mail in Odoo 19
        "web",
        "hr_expense",
        "maintenance",
        "project",
        "purchase",
    ],
    "external_dependencies": {
        "python": [
            "requests",
            "paho-mqtt",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/oauth_providers.xml",
        "views/res_config_settings_views.xml",
        "views/foundry_provider_config_views.xml",
        "views/doc_digitization_config_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
