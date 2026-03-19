# Checklist — odoo-ci-validation

- [ ] GitHub Actions workflow runs queried for target PR/commit
- [ ] All required status checks evaluated (lint, typecheck, test, build)
- [ ] Test output analyzed and failures classified per testing policy
- [ ] Build artifact produced successfully
- [ ] No GHAS secret scanning alerts on PR diff
- [ ] No critical dependency alerts
- [ ] Module test evidence exists (test_<module> database results)
- [ ] No pre-commit hooks bypassed
- [ ] All test failures classified (passes_locally, init_only, env_issue, migration_gap, real_defect)
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-ci-validation/`
