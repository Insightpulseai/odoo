# Copyright 2026 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "IPAI Web Branding",
    "summary": "InsightPulse AI login page branding and Odoo debranding",
    "version": "19.0.1.0.0",
    "category": "Website",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "views/login_templates.xml",
        "data/res_company_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ipai_web_branding/static/src/scss/login.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "development_status": "Beta",
}
