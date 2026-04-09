---
name: Odoo Security
description: Define access control lists, record rules, groups, field access, or review security posture. Use when creating or auditing Odoo permissions.
---

# Odoo Security

## Purpose

Implement correct access control for Odoo 18 CE models using groups, ACLs, and record rules.

## When to use

- Defining ACLs (`ir.model.access.csv`)
- Creating record rules (`ir.rule`)
- Designing security groups
- Reviewing privilege escalation risks
- Auditing `sudo()` usage

## Inputs or assumptions

- Every model must have at least one ACL entry
- Multi-company isolation via record rules when `company_id` field exists
- `sudo()` requires documented justification

## Source priority

1. Local security files in `addons/`
2. Odoo 18 CE security documentation
3. OCA security patterns

## Workflow

1. Define groups (user → manager hierarchy via `implied_ids`)
2. Create ACL entries for every model
3. Add record rules for multi-company isolation
4. Audit `sudo()` usage
5. Test as restricted user: `self.env(user=limited_user)`

## Access control layers

1. **Groups** — define user categories
2. **ACLs** — model-level CRUD permissions per group
3. **Record rules** — row-level filtering per group
4. **Field access** — field-level read/write restrictions (rare)

## Groups

```xml
<record id="group_my_user" model="res.groups">
    <field name="name">My Feature User</field>
    <field name="category_id" ref="base.module_category_services"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>

<record id="group_my_manager" model="res.groups">
    <field name="name">My Feature Manager</field>
    <field name="implied_ids" eval="[(4, ref('group_my_user'))]"/>
</record>
```

## ACLs (`ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_ipai_my_model,group_my_user,1,1,1,0
access_my_model_manager,my.model.manager,model_ipai_my_model,group_my_manager,1,1,1,1
```

## Record rules

```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: multi-company</field>
    <field name="model_id" ref="model_ipai_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

- `global=True` (no groups) applies to everyone including admin
- Group-scoped rules apply only to members of that group
- Multiple rules for the same group are OR-combined
- Rules across different groups are AND-combined

## Output format

Security XML + CSV files with proper group hierarchy, ACL entries, and record rules.

## Verification

1. Every new model has ACL entries in `security/ir.model.access.csv`
2. Record rules exist for multi-company isolation where needed
3. `sudo()` usage is documented and justified
4. Sensitive fields restricted to manager groups
5. Controller endpoints check user authentication

## Anti-patterns

- Granting `perm_unlink` to regular users unless deletion is a business requirement
- Using empty `group_id` (public access) without explicit justification
- Relying on UI hiding (`invisible`) as a security mechanism
- Using `sudo()` in user-facing flows to bypass access control
- Creating global record rules that accidentally restrict admin users
- Missing ACL entries (causes silent access denial, not a visible error)
