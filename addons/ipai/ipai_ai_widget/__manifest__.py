# © 2026 InsightPulse AI
# License LGPL-3.0-or-later
{
    "name": "IPAI AI Widget",
    "summary": "Ask AI widget for Odoo 19 CE — calls IPAI provider bridge (no IAP dependency)",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["mail", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ai_widget/static/src/xml/ask_ai_widget.xml",
            "ipai_ai_widget/static/src/js/ask_ai_widget.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    # Explicit: no odoo.com/iap dependency
    "external_dependencies": {"python": ["requests"]},
}
