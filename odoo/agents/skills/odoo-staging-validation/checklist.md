# Checklist — odoo-staging-validation

- [ ] Staging Container App running expected revision confirmed
- [ ] Staging database (odoo_staging) available and accessible
- [ ] Disposable test databases (test_<module>) created for each test run
- [ ] Automated tests executed with --test-enable
- [ ] Test output captured: pass count, fail count, skip count
- [ ] Every failure classified (passes_locally, init_only, env_issue, migration_gap, real_defect)
- [ ] No failures silently skipped
- [ ] Regression analysis against previous test run completed
- [ ] Production database (odoo) NOT used for any test
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-staging-validation/`
