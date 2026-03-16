# © 2026 InsightPulse AI
# License LGPL-3.0-or-later
{
    "name": "IPAI AI Widget",
    "summary": "Ask AI widget for Odoo 19 CE — calls IPAI provider bridge (no IAP dependency)",
    "version": "19.0.2.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["mail", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "data/presets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ai_widget/static/src/xml/ask_ai_widget.xml",
            "ipai_ai_widget/static/src/xml/composer_ai_templates.xml",
            "ipai_ai_widget/static/src/xml/composer_ai_patch.xml",
            "ipai_ai_widget/static/src/js/ask_ai_widget.js",
            "ipai_ai_widget/static/src/js/ai_inline_panel.js",
            "ipai_ai_widget/static/src/js/preset_chips.js",
            "ipai_ai_widget/static/src/js/composer_ai_action.js",
            "ipai_ai_widget/static/src/js/composer_ai_patch.js",
            "ipai_ai_widget/static/src/scss/ai_composer.scss",
        ],
    },
    "installable": False,
    "auto_install": False,
    "application": False,
    # DEPRECATED: Replaced by Foundry ask mode via ipai_odoo_copilot (2026-03-15)
    # See: ssot/governance/ai-consolidation-foundry.yaml
    "external_dependencies": {"python": ["requests"]},
}
