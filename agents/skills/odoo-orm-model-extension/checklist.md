# Checklist — odoo-orm-model-extension

- [ ] Target model identified and confirmed as CE-compatible (not Enterprise-only)
- [ ] Extension uses `_inherit` in an `ipai_*` module (not copy-paste)
- [ ] No files modified under `vendor/odoo/` or `addons/oca/`
- [ ] Class attribute order follows Odoo 18 convention (10-step order)
- [ ] Field names follow convention: `*_id` (M2O), `*_ids` (O2M/M2M), `is_*`/`has_*` (Boolean)
- [ ] Compute methods named `_compute_<field>` with `@api.depends`
- [ ] Inverse methods named `_inverse_<field>` if applicable
- [ ] Constraint methods named `_check_<field>` with `@api.constrains`
- [ ] SQL constraints use `_sql_constraints` list
- [ ] x2many writes use `Command` tuples (not raw tuples)
- [ ] Context changes use `with_context()` (never direct mutation)
- [ ] Translations use lazy `_('msg %s', arg)` (never f-strings or `.format()`)
- [ ] No `cr.commit()` calls
- [ ] Import order: stdlib, odoo core, odoo.addons (each block separated by blank line)
- [ ] Model file compiles with `python3 -m py_compile`
- [ ] Test install succeeds on disposable `test_<module>` DB
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-orm-model-extension/`
