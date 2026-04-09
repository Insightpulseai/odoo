---
name: odoo-views
description: Create or modify Odoo 18 CE XML views
triggers:
  - file_pattern: "addons/ipai/**/views/*.xml"
  - keywords: ["form view", "tree view", "kanban view", "search view"]
layer: A-domain
---

# Odoo 18 View Skill

When creating or modifying views:

1. XML ID pattern: `<model_name>_view_<type>` (e.g. `sale_order_view_form`)
2. Use `list` not `tree` — Odoo 18 renamed tree to list
3. Action XML ID: `<model_name>_action`
4. Menu XML ID: `<model_name>_menu`
5. CSS class prefix: `o_ipai_<module>_`
6. No `!important` unless overriding Odoo core
7. No ID selectors in CSS
8. Data file order in manifest: security groups → ACLs → data → views
