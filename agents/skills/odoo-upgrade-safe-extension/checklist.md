# Checklist — odoo-upgrade-safe-extension

- [ ] All model extensions use `_inherit` (not copy-paste of core code)
- [ ] No files modified under `vendor/odoo/`
- [ ] No files modified under `addons/oca/` (ipai_* override module created instead)
- [ ] No OCA files copied into `addons/ipai/`
- [ ] All view changes use inherited views with xpath (not replacement)
- [ ] Migration scripts exist in `migrations/<version>/` for schema changes
- [ ] `__manifest__.py` version follows `19.0.x.y.z`
- [ ] Dependencies are explicit and minimal
- [ ] No `cr.commit()` calls found
- [ ] No direct `env.context` mutation (uses `with_context()` instead)
- [ ] No f-string or `.format()` translations (uses lazy `_()` with positional args)
- [ ] x2many writes use `Command` tuples (not raw tuples)
- [ ] Odoo 19 `group_ids` used (not deprecated `groups_id`)
- [ ] `list` used in user-facing view references (not `tree`)
- [ ] Module installs cleanly on disposable test DB after changes
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-upgrade-safe-extension/`
