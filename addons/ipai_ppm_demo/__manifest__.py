# ipai_ppm_demo/__manifest__.py
{
    "name": "IPAI PPM Demo (Planview-style Seed)",
    "summary": "Seed data and basic models to demo Planview-style PPM dashboards in Odoo CE.",
    "version": "18.0.1.0.0",
    "author": "InsightPulse AI",
    "license": "AGPL-3",
    "website": "https://insightpulseai.com",
    "category": "Project",
    "depends": [
        "project",
        "hr",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ppm_menus.xml",
        "views/ppm_models_views.xml",
        "views/ppm_dashboard_action.xml",
        "data/ppm_demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ppm_demo/static/lib/echarts.min.js",
            "ipai_ppm_demo/static/src/js/ppm_dashboard.js",
            "ipai_ppm_demo/static/src/xml/ppm_dashboard.xml",
            "ipai_ppm_demo/static/src/css/ppm_dashboard.css",
        ],
    },
    "application": True,
}
