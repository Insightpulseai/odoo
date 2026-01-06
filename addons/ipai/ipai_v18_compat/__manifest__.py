# -*- coding: utf-8 -*-
{
    "name": "IPAI Odoo 18 Compatibility Fixes",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Patches legacy view_mode 'tree' → 'list' and fixes broken kanbans",
    "description": """
IPAI Odoo 18 Compatibility Module
=================================

This module automatically fixes common Odoo 18 breaking changes:

1. **view_mode tree → list**: Odoo 18 renamed 'tree' to 'list' in ir.actions.act_window.
   This module patches all actions that still reference 'tree'.

2. **Kanban card template**: Odoo 18 requires t-name="card" in kanban templates.
   This module can detect and report broken kanban views.

The fixes run automatically:
- On module install (post_init_hook)
- On module upgrade (migrations/post-migrate.py)

You can also run the fix manually via the wrapper script:
    python addons/ipai/scripts/fix_odoo18_views.py

""",
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
