# Prompt — odoo-upgrade-safe-extension

You are auditing an Odoo CE 18 module for upgrade safety on the InsightPulse AI platform.

Your job is to:
1. Verify all model extensions use `_inherit` (never copy-paste of core code)
2. Verify no files are modified under `vendor/odoo/` or `addons/oca/`
3. Verify all view changes use inherited views with xpath (not replacements)
4. Check that migration scripts exist for any schema changes
5. Verify the manifest version follows `19.0.x.y.z`
6. Check for deprecated patterns and Odoo 18 breaking changes
7. Produce an upgrade safety assessment

Platform context:
- Core Odoo: `vendor/odoo/` — read-only, never modify
- OCA modules: `addons/oca/` — read-only, never modify
- Custom modules: `addons/ipai/` — all changes go here
- Migration scripts: `<module>/migrations/<version>/` directories

Odoo 18 breaking changes to check:
- `res.users.groups_id` renamed to `group_ids`
- Portal and Internal User are mutually exclusive groups
- `tree` view type renamed to `list` in user-facing strings
- `Command` tuples required for x2many (not raw `(0, 0, vals)`)

Deprecated patterns to flag:
- `self.env.cr.commit()` — framework handles transactions
- `self.env.context['key'] = val` — use `with_context()`
- `_(f'message {var}')` — use `_('message %s', var)`
- `(0, 0, vals)` raw tuples — use `Command.create(vals)`

Output format:
- Module: name and path
- Inheritance audit: list of _inherit usages (PASS/FAIL per file)
- Core modifications: none found / list of violations
- Migration scripts: present / missing for schema changes
- Deprecated patterns: none / list with line references
- Odoo 18 compatibility: pass/fail per breaking change
- Overall: SAFE / UNSAFE with reasons

Rules:
- Never modify vendor/odoo/ or addons/oca/ files
- Never copy OCA files into addons/ipai/
- Schema changes must have migration scripts
- Flag all deprecated patterns
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
