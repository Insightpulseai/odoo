# Prompt — odoo-module-scaffolding

You are scaffolding a new Odoo CE 19 module for the InsightPulse AI platform.

Your job is to:
1. Validate the module name follows `ipai_<domain>_<feature>` convention
2. Create the directory structure under `addons/ipai/`
3. Write `__manifest__.py` with version `19.0.1.0.0`, license `LGPL-3`, minimal explicit dependencies
4. Write `__init__.py` files importing the models package
5. Create `models/` with a stub model class following Odoo 19 class attribute order
6. Create `security/ir.model.access.csv` with header and ACL rows (all 4 CRUD columns)
7. Create `views/` with stub view XML and menu items following XML ID conventions
8. Create `tests/__init__.py` and `tests/test_<module>.py` stub
9. Verify the manifest is valid Python (`python3 -m py_compile`)
10. Verify no Enterprise or IAP dependencies exist

Platform context:
- Module path: `addons/ipai/ipai_<domain>_<feature>/`
- Naming: `ipai_<domain>_<feature>` (e.g. `ipai_finance_ppm`, `ipai_ai_tools`)
- Version: `19.0.x.y.z`
- License: `LGPL-3`
- Data order in manifest: security groups, ACLs, data, views

Output format:
- Module path: full path created
- Files created: list with purpose
- Manifest validation: pass/fail
- Dependency check: pass/fail (no EE deps)
- Evidence: file tree and py_compile result

Rules:
- Never include Enterprise module dependencies
- Never include odoo.com IAP dependencies
- Always provide all 4 CRUD columns in ir.model.access.csv
- ID pattern for ACLs: `access_<model>_<group>`
- Follow Odoo 19 class attribute order strictly
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
