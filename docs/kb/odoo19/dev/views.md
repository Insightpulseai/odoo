# Backend Views: Form, List, Kanban, Search

## What it is

XML definitions that declare how data is presented in the backend UI.

## Key concepts

- **Form View:** Detailed record editing.
- **Tree (List) View:** Tabular display of multiple records.
- **Kanban View:** Card-based display, often grouped by stage.
- **Search View:** Defines filters and grouping options.

## Implementation patterns

### Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="value"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

## Gotchas

- **Inheritance:** `inherit_id` allows modifying standard views via XPath. Be specific with selectors to avoid breaking on unrelated changes.
- **Attributes:** Common attributes: `invisible`, `readonly`, `required`.

## References

- [Odoo Views Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html)
