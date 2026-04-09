---
name: Odoo Security
description: Use when defining access control lists, record rules, groups, field access, or reviewing security posture.
---

# Odoo Security

## When to use

- Defining ACLs (`ir.model.access.csv`)
- Creating record rules (`ir.rule`)
- Designing security groups
- Reviewing privilege escalation risks
- Auditing `sudo()` usage

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

Use implied groups for role hierarchy (manager implies user).

## ACLs (`ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_ipai_my_model,group_my_user,1,1,1,0
access_my_model_manager,my.model.manager,model_ipai_my_model,group_my_manager,1,1,1,1
```

- Every model must have at least one ACL rule
- Use `group_id:id` empty for public access (rare, avoid)
- Separate user vs manager permissions explicitly

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

## Checklist

1. Does every new model have ACL entries in `security/ir.model.access.csv`?
2. Are record rules needed for multi-company isolation?
3. Is `sudo()` used? Document why and confirm it cannot be avoided
4. Are sensitive fields (bank accounts, passwords) restricted to manager groups?
5. Do controller endpoints check user authentication?

## Do not

- Grant `perm_unlink` to regular users unless deletion is a business requirement
- Use empty `group_id` (public access) without explicit justification
- Rely on UI hiding (`invisible`) as a security mechanism
- Use `sudo()` in user-facing flows to bypass access control
- Create global record rules that accidentally restrict admin users
