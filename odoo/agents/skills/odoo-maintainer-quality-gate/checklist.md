# Checklist — odoo-maintainer-quality-gate

- [ ] 19.0 branch exists in OCA repository
- [ ] CI is green on 19.0 branch
- [ ] `development_status` >= `Stable` in `__manifest__.py`
- [ ] `development_status` >= `Mature` if critical path module
- [ ] Test install succeeds on disposable DB (`test_<module>`)
- [ ] No conflicts with existing ipai_* modules
- [ ] No Enterprise module dependencies
- [ ] No odoo.com IAP calls
- [ ] No transitive dependencies on Beta modules
- [ ] Documented in `config/addons.manifest.yaml` with repo, tier, provenance
- [ ] Coverage percentage reviewed
- [ ] Contributor and review history checked
- [ ] Adoption verdict issued (APPROVE / REJECT / CONDITIONAL)
- [ ] Evidence captured in `docs/evidence/{stamp}/oca-governance/odoo-maintainer-quality-gate/`
