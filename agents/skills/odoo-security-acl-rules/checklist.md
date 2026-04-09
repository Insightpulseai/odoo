# Checklist — odoo-security-acl-rules

- [ ] Security groups defined in `security/security.xml` with category
- [ ] Group hierarchy correct (manager implies user via `implied_ids`)
- [ ] `ir.model.access.csv` has header row with all columns
- [ ] Every model has at least one ACL row
- [ ] All ACL rows have all 4 CRUD columns (perm_read, perm_write, perm_create, perm_unlink)
- [ ] ACL ID pattern: `access_<model>_<group>`
- [ ] No full CRUD granted to public/portal without explicit justification
- [ ] Portal and Internal User groups are mutually exclusive (Odoo 18 rule)
- [ ] Multi-company record rules use correct domain: `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]`
- [ ] Record rules have correct `model_id` reference
- [ ] Security XML listed first in `__manifest__.py` data section
- [ ] No core security files modified (use override module)
- [ ] Access tested on disposable `test_<module>` DB
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-dev/odoo-security-acl-rules/`
