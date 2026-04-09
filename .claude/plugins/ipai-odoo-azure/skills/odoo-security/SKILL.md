---
name: odoo-security
description: Create Odoo 18 CE security files (ACLs, record rules, groups)
triggers:
  - file_pattern: "addons/ipai/**/security/*"
  - keywords: ["ir.model.access", "ir.rule", "security group"]
layer: A-domain
---

# Odoo 18 Security Skill

1. `ir.model.access.csv`: always provide all 4 CRUD columns
2. ID pattern: `access_<model>_<group>`
3. Record rule pattern: `<model>_rule_<scope>`
4. Group pattern: `group_<name>`
5. Never leave ACL rows without explicit group assignment
6. Test with `--test-enable` to verify access control
