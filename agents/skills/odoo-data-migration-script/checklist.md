# Checklist — odoo-data-migration-script

- [ ] `migrations/<version>/` directory created in module
- [ ] Version in directory name matches `__manifest__.py` version
- [ ] `migrate(cr, version)` function defined as entry point
- [ ] Fresh install guard: `if not version: return` at top of migrate()
- [ ] Pre-migration uses raw SQL only (ORM not loaded at this stage)
- [ ] Post-migration uses ORM operations (env available via `api.Environment(cr, SUPERUSER_ID, {})`)
- [ ] No `cr.commit()` calls in migration scripts
- [ ] SQL uses `IF NOT EXISTS` / `WHERE NOT EXISTS` for idempotency
- [ ] Default values provided for new required columns
- [ ] Logging added via `_logger.info()` for migration progress
- [ ] Tested on disposable `test_<module>` DB with existing data (forward migration)
- [ ] Tested on empty DB (fresh install path)
- [ ] Both pre and post migration complete without errors
- [ ] No prod/dev/staging databases used for testing
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-data-migration-script/`
