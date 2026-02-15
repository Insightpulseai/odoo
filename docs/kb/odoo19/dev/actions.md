# Backend Actions: Window, Server, Automated

## What it is

Actions define "what happens" when a user clicks a menu item or button. They often open Views or execute Python code.

## Key concepts

- **Window Action (ir.actions.act_window):** Opens a specific view for a model.
- **Server Action (ir.actions.server):** Executes Python code directly.
- **Automated Action:** Triggers server actions based on database events (create/write).

## Implementation patterns

### Window Action

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
</record>
```

## Gotchas

- **Context:** Passing `context` in the action is crucial for setting default values (`default_field=value`) or changing view behavior.
- **Domain:** Static filters applied when opening the view.

## References

- [Odoo Actions Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)
