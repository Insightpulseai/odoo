{
    "name": "IPAI Web Fluent 2 Theme Layer",
    "version": "18.0.1.0.0",
    "category": "Themes/Backend",
    "summary": "Fluent 2 design tokens + UI styling for Odoo CE 18 backend (and optional frontend/login).",
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": ["web", "mail"],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        # Backend webclient (where you want Planner-like UI)
        "web.assets_backend": [
            "ipai_web_fluent2/static/src/scss/fluent2_tokens.scss",
            "ipai_web_fluent2/static/src/scss/backend.scss",
            "ipai_web_fluent2/static/src/js/fluent2_boot.js",
        ],
        # Optional: login page / public web pages (keep if you want consistent brand)
        "web.assets_frontend": [
            "ipai_web_fluent2/static/src/scss/fluent2_tokens.scss",
            "ipai_web_fluent2/static/src/scss/frontend.scss",
        ],
    },
    "installable": True,
    "application": False,
}
