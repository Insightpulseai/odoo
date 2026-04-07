# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "InsightPulseAI Login Branding",
    "summary": "Production login page with Entra ID + Google sign-in and debranding",
    "version": "18.0.4.0.0",
    "category": "Website",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "web",
        "website",
        "auth_oauth",
        "auth_oidc",
        "portal_odoo_debranding",
        "disable_odoo_online",
        "remove_odoo_enterprise",
    ],
    "assets": {
        "web.assets_frontend": [
            "ipai_web_branding/static/src/scss/login.scss",
        ],
    },
    "data": [
        "data/res_company_data.xml",
        "data/auth_provider_data.xml",
        "data/website_data.xml",
        "views/login_templates.xml",
        "views/website_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
