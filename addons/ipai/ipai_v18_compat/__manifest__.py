# -*- coding: utf-8 -*-
{
    "name": "IPAI Odoo 18 Compatibility Fixes",
    "summary": "Post-migrate hotfixes for Odoo 18 view_mode rename (tree->list) and kanban card template issues",
    "description": """
IPAI Odoo 18 Compatibility Fixes
================================

This module provides automatic fixes for breaking changes in Odoo 18:

1. **tree -> list View Mode Rename**
   Odoo 18 renamed the 'tree' view mode to 'list'. This module automatically
   updates all ir.actions.act_window records that still use 'tree' in their
   view_mode field.

2. **Kanban Card Template Requirement**
   Odoo 18 requires kanban views to have a `t-name="card"` template. This module
   detects kanban views missing this template and optionally deactivates them.

Usage
-----

**Installation:**
    odoo -d <database> -i ipai_v18_compat --stop-after-init

**Re-run migration:**
    odoo -d <database> -u ipai_v18_compat --stop-after-init

**Enable auto-deactivation of broken kanban views:**
    Set system parameter: ipai_v18_compat.deactivate_broken_kanban = 1

Configuration
-------------

System Parameters:
- ipai_v18_compat.deactivate_broken_kanban: Set to "1" to automatically
  deactivate kanban views missing the card template.
    """,
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
