{
    "name": "IPAI Service Calculator",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Wizard to generate SO lines from predefined service packs",
    "author": "InsightPulse AI, Odoo Community Association (OCA)",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "sale_order_type",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_service_pack_views.xml",
        "wizard/ipai_service_calculator_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Beta",
}
