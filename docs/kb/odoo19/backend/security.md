# Odoo 19 Security

## Concept

Odoo security is a multi-layered system comprising Access Control Lists (ACLs), Record Rules, and Field Access rights. It follows a "deny by default" philosophy, except for Record Rules which are "default allow" if no rule matches.

## Layers

1. **Access Rights (ACL):** Grants model-level CRUD access (e.g., "Can group `User` read model `sale.order`?").
   - Defined in `ir.model.access.csv`
2. **Record Rules:** Filters which _specific rows_ a user can access (e.g., "Can user read `sale.order` where `user_id = me`?").
   - Defined in XML data records (`ir.rule`).
3. **Field Access:** Restricts access to specific columns.
   - Defined in Python: `groups="base.group_user"`.

## Extension Pattern

**Adding ACL (ir.model.access.csv):**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

**Adding Record Rule:**

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User specific</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

## Common Mistakes

- **Global Rules vs Group Rules:** Global rules (no group assigned) are INTERSECTED (AND) with group rules. Group rules are UNIONED (OR) with other group rules.
  - _Pitfall:_ A global rule `[('id', '=', False)]` will block EVERYONE, including admins, unless `sudo()` is used.
- **Bypassing ORM:** Raw SQL (`self.env.cr.execute`) bypasses all security rules.
- **Unsafe Public Methods:** Any method not starting with `_` is callable via XML-RPC. Always check `self.check_access_rights()` or rely on implicit ORM checks.

## Agent Notes

- `sudo()` switches to the Superuser, bypassing ALL ACL and Record Rules. Use with extreme caution.
- Multicompany security is largely handled via Record Rules filtering on `company_id`.

## Source Links

- [Security in Odoo](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
