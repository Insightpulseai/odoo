{
    "name": "IPAI Shelf.nu Connector",
    "summary": "Bidirectional sync between Odoo equipment/assets and Shelf.nu asset management",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "maintenance",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/maintenance_equipment_views.xml",
        "views/shelf_sync_log_views.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
}
