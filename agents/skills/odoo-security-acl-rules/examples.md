# Examples — odoo-security-acl-rules

## Example 1: Security for ipai_finance_ppm module

**Input**: Define security for `ipai.finance.report` model with user and manager groups

**Output** — security/security.xml:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_ipai_finance" model="ir.module.category">
        <field name="name">IPAI Finance</field>
    </record>

    <record id="group_ipai_finance_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_ipai_finance"/>
    </record>

    <record id="group_ipai_finance_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_ipai_finance"/>
        <field name="implied_ids" eval="[(4, ref('group_ipai_finance_user'))]"/>
    </record>

    <record id="ipai_finance_report_rule_multi_company" model="ir.rule">
        <field name="name">Finance Report: multi-company</field>
        <field name="model_id" ref="model_ipai_finance_report"/>
        <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
    </record>
</odoo>
```

**Output** — security/ir.model.access.csv:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_finance_report_user,ipai.finance.report user,model_ipai_finance_report,group_ipai_finance_user,1,0,0,0
access_ipai_finance_report_manager,ipai.finance.report manager,model_ipai_finance_report,group_ipai_finance_manager,1,1,1,1
```

- Groups: PASS (2 groups, correct hierarchy)
- ACLs: PASS (2 rows, all 4 CRUD columns)
- Multi-company rule: PASS
- Access test: PASS

## Example 2: Missing CRUD column detected

**Input**: ACL CSV with only 3 columns (missing perm_unlink)

**Output**:
- Validation: FAIL
- Reason: `perm_unlink` column missing — all 4 CRUD columns are required
- Recommendation: Add `perm_unlink` column to every row

## Example 3: Portal/Internal exclusivity violation

**Input**: Assign same user to both Portal and Internal User groups

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Odoo 19 makes Portal and Internal User mutually exclusive
- Recommendation: Choose one group per user; use record rules for cross-boundary access
