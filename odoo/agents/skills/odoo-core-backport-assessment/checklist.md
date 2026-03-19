# Checklist — odoo-core-backport-assessment

- [ ] Core behavior issue clearly identified
- [ ] Upstream Odoo fix status checked (merged/pending/not addressed)
- [ ] OCB branch for current version inspected for existing backport
- [ ] Change classified as generic or project-specific
- [ ] Recommendation issued (OCB backport / ipai_* override / wait)
- [ ] No direct modification to vendor/odoo/ proposed
- [ ] No file copying from OCA into addons/ipai/ proposed
- [ ] ipai_* override uses proper _inherit pattern if recommended
- [ ] Risk level assigned
- [ ] Evidence captured in `docs/evidence/{stamp}/oca-governance/odoo-core-backport-assessment/`
