# Examples — odoo-code-review-judge

## Example 1: Clean module — PASS

**Input**: PR adds `ipai_finance_dashboard` module with standard structure.

**Review**:
```
Verdict: PASS
Risk level: low

Violations: none

Module structure:
- __manifest__.py: version 19.0.1.0.0, license LGPL-3 — PASS
- Directory layout: models/, views/, security/, data/ — PASS
- Data order: security.xml, ir.model.access.csv, dashboard_data.xml, dashboard_views.xml — PASS

Python style:
- Import ordering: correct (stdlib → odoo → odoo.addons) — PASS
- Lazy translation: _('Dashboard %s not found', name) — PASS
- Model attribute order: correct — PASS
- Field naming: company_id (M2O), line_ids (O2M), is_published (bool) — PASS

XML structure:
- XML IDs: finance_dashboard_view_form, finance_dashboard_action — PASS
- No deprecated tree views — PASS

Transaction safety:
- No cr.commit() — PASS
- No raw SQL — PASS

Extendability:
- Largest method: 18 lines — PASS
- Hook points: _prepare_dashboard_data() available for override — PASS

Evidence: models/finance_dashboard.py:1-85, views/finance_dashboard_views.xml:1-60
```

## Example 2: Module with transaction violation — FAIL

**Input**: PR adds `ipai_bulk_import` module with `cr.commit()` in import loop.

**Review**:
```
Verdict: FAIL
Risk level: critical

Violations:
- [CRITICAL] models/bulk_import.py:47 — Rule 2 (transaction safety) — cr.commit() inside
  for loop without justification. Breaks ORM transaction rollback safety.
  Line: `self.env.cr.commit()  # save progress`
- [HIGH] models/bulk_import.py:32 — Rule 3 (exception handling) — bare except clause
  catches all exceptions silently.
  Line: `except: pass`
- [MEDIUM] models/bulk_import.py:1-5 — Rule 4 (import ordering) — odoo imports mixed
  with stdlib imports.

Required fixes:
1. Remove cr.commit() at line 47 — use ORM batch operations or, if truly needed for
   memory management in large imports, add explicit justification comment explaining why
   and document the rollback implications. (models/bulk_import.py:47)
2. Replace bare except with specific exception catch (models/bulk_import.py:32)
3. Fix import ordering (models/bulk_import.py:1-5)

Upgrade safety:
- No Odoo 19 specific issues found

Evidence:
- models/bulk_import.py:47: `self.env.cr.commit()  # save progress`
- models/bulk_import.py:32: `except: pass`
- models/bulk_import.py:1-5: `import logging\nfrom odoo import models\nimport os`
```

## Example 3: Module with structure violations — FAIL

**Input**: PR adds `ipai_crm_extension` with multiple structure and naming violations.

**Review**:
```
Verdict: FAIL
Risk level: high

Violations:
- [HIGH] __manifest__.py — Rule 6 (module structure) — version is "1.0" instead of
  "19.0.1.0.0". License field missing.
- [HIGH] views/crm.xml — Rule 5 (XML naming) — file should be named crm_extension_views.xml
- [HIGH] views/crm.xml:15 — Rule 5 (XML naming) — XML ID "crm_form" should be
  "crm_extension_view_form"
- [HIGH] views/crm.xml:40 — Rule 5 (Odoo 19) — deprecated tree view type used. Must be
  "list" in Odoo 19.
  Line: `<record id="crm_tree" model="ir.ui.view">`
- [MEDIUM] models/crm_lead.py:25 — Rule 4 (translation) — f-string inside _()
  Line: `raise UserError(_(f'Lead {self.name} cannot be archived'))`
- [MEDIUM] models/crm_lead.py — Rule 4 (attribute order) — fields declared before
  _name and _inherit
- [LOW] security/ir.model.access.csv — Rule 5 (ACL naming) — ID "access_crm_1" should
  follow "access_<model>_<group>" pattern

Required fixes:
1. Fix manifest: version "19.0.1.0.0", add license "LGPL-3" (__manifest__.py)
2. Rename views/crm.xml to views/crm_extension_views.xml
3. Fix XML IDs to follow naming convention (views/crm_extension_views.xml)
4. Replace tree with list (views/crm_extension_views.xml:40)
5. Replace f-string with lazy interpolation: _('Lead %s cannot be archived', self.name)
   (models/crm_lead.py:25)
6. Reorder model class attributes (models/crm_lead.py)
7. Fix ACL ID naming (security/ir.model.access.csv)

Upgrade safety:
- BLOCKING: tree view type must be changed to list for Odoo 19 compatibility
- Check: if module references groups_id, change to group_ids

Evidence:
- __manifest__.py: `{'version': '1.0', 'name': 'CRM Extension'}`
- views/crm.xml:40: `<record id="crm_tree" model="ir.ui.view">`
- models/crm_lead.py:25: `raise UserError(_(f'Lead {self.name} cannot be archived'))`
```
