# Checklist — odoo-upgrade-rehearsal

- [ ] Disposable database created (never production or canonical dev)
- [ ] Database naming follows `test_upgrade_{source}_to_{target}` pattern
- [ ] OpenUpgrade migration scripts applied
- [ ] Custom ipai_* migration scripts applied
- [ ] Module install status verified for every module
- [ ] Record counts compared pre- and post-migration
- [ ] Key relational fields validated (partner links, account references)
- [ ] Automated tests executed post-migration
- [ ] Every failure classified (passes locally / init only / env issue / migration gap / real defect)
- [ ] No silent skips — all modules accounted for
- [ ] Raw test output saved to evidence directory
- [ ] Evidence captured in `docs/evidence/{stamp}/oca-governance/odoo-upgrade-rehearsal/`
