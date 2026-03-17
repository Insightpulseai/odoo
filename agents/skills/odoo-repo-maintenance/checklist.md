# Checklist — odoo-repo-maintenance

- [ ] Module manifest version follows `{odoo_version}.x.y.z` pattern
- [ ] License is `LGPL-3` or `AGPL-3`
- [ ] `development_status` field is present and accurate
- [ ] Dependencies are explicit and minimal
- [ ] `.pre-commit-config.yaml` exists and includes OCA hooks
- [ ] Pre-commit hook revisions are current
- [ ] README generated via oca-gen-addon-readme (not hand-written)
- [ ] CI passes on target branch
- [ ] `.gitmodules` pins are within 30 days of current
- [ ] No direct modifications to OCA source proposed
- [ ] Modules below Stable flagged for production exclusion
- [ ] Evidence captured in `docs/evidence/{stamp}/oca-governance/odoo-repo-maintenance/`
