# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM Dashboard",
    "version": "18.0.1.0.0",
    "summary": "Month-end & BIR calendar dashboard (Gantt + calendar graph)",
    "category": "Accounting/Reporting",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "data": [
        "views/ipai_finance_ppm_dashboard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/ipai_finance_ppm_dashboard/static/lib/echarts.min.js",
            "/ipai_finance_ppm_dashboard/static/src/js/ppm_dashboard.js",
            "/ipai_finance_ppm_dashboard/static/src/xml/ppm_dashboard_templates.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
