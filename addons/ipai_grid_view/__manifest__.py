# -*- coding: utf-8 -*-
{
    "name": "IPAI Grid/List View",
    "version": "18.0.1.0.0",
    "category": "Productivity/Views",
    "summary": "Advanced grid and list view with sorting, filtering, and bulk actions",
    "description": """
IPAI Grid/List View
===================

A comprehensive grid/list view implementation for Odoo 18 featuring:

- **Grid Display**: Configurable column layouts with resize and reorder
- **Search & Filtering**: Real-time keyword search and advanced filter panel
- **Sorting**: Multi-column sort with visual indicators
- **Selection & Bulk Actions**: Row selection with bulk operation support
- **View Switching**: Seamless toggle between list and kanban views
- **Responsive Design**: Horizontal scroll and mobile adaptation
- **Activity Integration**: Activity buttons and status indicators

Technical Stack:
- OWL Components for reactive UI
- Server-side pagination and filtering
- JSON-based configuration storage
- SCSS styling with CSS variables
    """,
    "author": "IPAI Team",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/grid_view_views.xml",
        "views/grid_column_views.xml",
        "views/grid_filter_views.xml",
        "data/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_grid_view/static/src/scss/grid_view.scss",
            "ipai_grid_view/static/src/js/grid_view.js",
            "ipai_grid_view/static/src/js/grid_controller.js",
            "ipai_grid_view/static/src/js/grid_renderer.js",
            "ipai_grid_view/static/src/js/grid_model.js",
            "ipai_grid_view/static/src/xml/grid_templates.xml",
        ],
    },
    "demo": [
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
