# Checklist — odoo-branch-series-governance

- [ ] Target Odoo version identified
- [ ] repo-maintainer-conf checked for branch generation rules
- [ ] OCB branch exists for target version
- [ ] CI tooling verified for new series (pre-commit, pylint-odoo, linting)
- [ ] oca-github-bot configuration includes new series
- [ ] Migration issues created per OCA process for dependent repos
- [ ] OCA repos in addons manifest checked for target branch availability
- [ ] Missing branches inventoried
- [ ] Series readiness classification issued (ready / not ready / partial)
- [ ] No branches created without CI tooling support
- [ ] Evidence captured in `docs/evidence/{stamp}/oca-governance/odoo-branch-series-governance/`
