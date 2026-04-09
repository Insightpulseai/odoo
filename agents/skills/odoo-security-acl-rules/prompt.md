# Prompt — odoo-security-acl-rules

You are implementing security for an Odoo CE 19 module on the InsightPulse AI platform.

Your job is to:
1. Define security groups in `security/security.xml` with proper category and hierarchy
2. Create `security/ir.model.access.csv` with all 4 CRUD columns for every model
3. Define record rules for multi-company isolation where applicable
4. Ensure group hierarchy is correct (manager implies user via `implied_ids`)
5. Verify Portal and Internal User groups are mutually exclusive
6. Test access control on a disposable database

Platform context:
- Security files: `security/security.xml` (groups, rules), `security/ir.model.access.csv` (ACLs)
- Manifest data order: security groups first, then ACLs, then data, then views
- Multi-company: most modules need `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]`

ACL CSV format:
```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_<model>_<group>,<description>,model_<model>,<group_xmlid>,1,1,1,0
```

Security group XML:
```xml
<record id="group_<name>_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_xmlid"/>
</record>
<record id="group_<name>_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="module_category_xmlid"/>
    <field name="implied_ids" eval="[(4, ref('group_<name>_user'))]"/>
</record>
```

Output format:
- Groups defined: list with XML IDs and hierarchy
- ACL rows: count and models covered
- Record rules: list with domain expressions
- Mutual exclusivity check: pass/fail (Portal vs Internal)
- Access test: pass/fail on disposable DB
- Evidence: install log and access test results

Rules:
- Always provide all 4 CRUD columns in ir.model.access.csv
- ACL ID pattern: `access_<model>_<group>`
- Never grant full CRUD to public/portal without justification
- Portal and Internal User are mutually exclusive in Odoo 18
- Security XML listed first in manifest data section
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
