# Prompt — odoo-orm-model-extension

You are extending an Odoo CE 18 model for the InsightPulse AI platform.

Your job is to:
1. Identify the target model and verify it exists in CE (not Enterprise-only)
2. Create an inherited model class using `_inherit` in an `ipai_*` module
3. Add fields in correct order: related, then computed, then stored
4. Implement compute methods with `@api.depends` decorators
5. Implement constraints with `@api.constrains` decorators
6. Add SQL constraints via `_sql_constraints`
7. Use Command tuples for any x2many write operations
8. Verify the model compiles and installs cleanly

Platform context:
- Custom modules: `addons/ipai/ipai_<domain>_<feature>/`
- OCA modules: `addons/oca/` — never modify, use `_inherit` overrides
- Core Odoo: `vendor/odoo/` — never modify

Odoo 18 class attribute order (strict):
1. Private attributes (_name, _description, _inherit, _order)
2. Default methods
3. Field declarations
4. SQL constraints
5. Compute, inverse, search methods
6. Selection methods
7. Constrains and onchange methods
8. CRUD methods (create, read, write, unlink)
9. Action methods
10. Business methods

Output format:
- Model: _name and _inherit values
- Fields added: list with types
- Methods added: list with decorators
- Compilation: pass/fail
- Test install: pass/fail on disposable DB
- Evidence: py_compile result and install log

Rules:
- Never modify files under vendor/odoo/ or addons/oca/
- Never copy OCA files — use _inherit
- Never call cr.commit() — ORM handles transactions
- Never mutate self.env.context — use with_context()
- Use Command tuples for x2many: Command.create(), Command.link(), Command.set()
- Use recordset methods: mapped(), filtered(), sorted()
- Use lazy translation: _('message %s', arg) — never f-strings or .format()
- Prefer inherited extension over core patching
