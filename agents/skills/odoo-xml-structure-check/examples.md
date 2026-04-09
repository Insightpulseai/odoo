# Examples — odoo-xml-structure-check

## Example 1: Compliant XML — PASS

**Input**: `ipai_helpdesk/views/helpdesk_ticket_views.xml` and `__manifest__.py`.

**Review**:
```
XML Compliance Report

Violations: none

Details:
- File naming: views/helpdesk_ticket_views.xml — PASS
- XML IDs:
  - helpdesk_ticket_view_form — PASS
  - helpdesk_ticket_view_list — PASS
  - helpdesk_ticket_view_search — PASS
  - helpdesk_ticket_view_kanban — PASS
  - helpdesk_ticket_action — PASS
  - helpdesk_ticket_menu — PASS
- Record formatting: one attribute per line, 4-space indent — PASS
- Manifest data order: security/security.xml, security/ir.model.access.csv,
  data/helpdesk_data.xml, views/helpdesk_ticket_views.xml — PASS
- Odoo 18: no deprecated tree views — PASS
- ACL CSV: proper header, all CRUD columns, ID pattern access_helpdesk_ticket_user — PASS

Upgrade safety: no issues
```

## Example 2: Deprecated tree views — FAIL

**Input**: `ipai_project_ext/views/project_views.xml` with tree views.

**Review**:
```
XML Compliance Report

Violations:
- [HIGH] views/project_views.xml:12 — deprecated tree view type
  Code: `<record id="project_task_tree" model="ir.ui.view">`
  Fix: rename XML ID to `project_task_view_list`

- [HIGH] views/project_views.xml:18 — deprecated <tree> tag
  Code: `<field name="arch" type="xml"><tree string="Tasks">`
  Fix: replace `<tree>` with `<list>`

- [HIGH] views/project_views.xml:45 — deprecated tree reference in action
  Code: `<field name="view_mode">tree,form,kanban</field>`
  Fix: replace `tree` with `list`: `<field name="view_mode">list,form,kanban</field>`

- [MEDIUM] views/project_views.xml:8 — XML ID does not follow convention
  Current: `project_task_tree`
  Expected: `project_task_view_list`

Fix suggestions:
1. Replace all tree references with list (lines 12, 18, 45)
2. Rename XML ID from project_task_tree to project_task_view_list (line 12)
3. Update any references to this XML ID in other files

Upgrade safety:
- BLOCKING: tree→list migration required for Odoo 18. Module will not load correctly
  with deprecated tree views in Odoo 18.
```

## Example 3: Multiple structure violations — FAIL

**Input**: `ipai_warehouse_ext/` module with multiple XML and manifest issues.

**Review**:
```
XML Compliance Report

Violations:
- [HIGH] views/warehouse.xml — incorrect file naming
  Current: views/warehouse.xml
  Expected: views/warehouse_ext_views.xml (or views/stock_warehouse_views.xml)

- [HIGH] security/ir.model.access.csv:2 — missing CRUD columns
  Current: `access_wh_1,warehouse access,model_stock_warehouse,base.group_user,1,1`
  Expected: all 4 columns (perm_read, perm_write, perm_create, perm_unlink)
  Fix: `access_stock_warehouse_user,stock.warehouse user,model_stock_warehouse,base.group_user,1,1,0,0`

- [HIGH] security/ir.model.access.csv:2 — incorrect ID pattern
  Current: `access_wh_1`
  Expected: `access_stock_warehouse_user`

- [MEDIUM] __manifest__.py — incorrect data file ordering
  Current:
    'data': [
        'views/warehouse.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/warehouse_data.xml',
    ]
  Expected:
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/warehouse_data.xml',
        'views/warehouse_ext_views.xml',
    ]

- [MEDIUM] views/warehouse.xml:5 — multiple attributes on one line
  Code: `<record id="wh_form" model="ir.ui.view" name="warehouse form">`
  Fix: one attribute per line

- [LOW] views/warehouse.xml:5 — XML ID does not follow convention
  Current: `wh_form`
  Expected: `stock_warehouse_view_form`

Fix suggestions:
1. Rename views/warehouse.xml to views/warehouse_ext_views.xml
2. Fix ACL CSV: add missing columns, fix ID pattern
3. Reorder manifest data key
4. Fix XML ID naming throughout
5. Format records with one attribute per line

Upgrade safety:
- No tree→list issues found
- Verify no groups_id references in Python code
```
