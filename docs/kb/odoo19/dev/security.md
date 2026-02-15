# Backend Security: ACLs, Record Rules

## What it is

Odoo's security mechanism controls user access to data at the model (ACL) and record (Record Rules) levels.

## Key concepts

- **Access Control Lists (ACLs):** Define Create, Read, Write, Unlink (CRUD) permissions for groups on a model. Defined in `ir.model.access.csv`.
- **Record Rules:** Domain filters that restrict access to specific rows based on dynamic conditions (e.g., "User can only see their own documents").
- **Groups:** Users are assigned to groups that inherit permissions.

## Implementation patterns

### ACL (`ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

### Record Rule (XML)

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User own documents</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Gotchas

- **Superuser:** The `admin` user (ID 1) bypasses all security rules.
- **Global Rules:** Rules with no group assigned apply to EVERYONE (including employees and external users).
- **Rule Combination:** Rules within the same group are combined with OR. Rules across different groups are combined with AND.

## References

- [Odoo Security Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
