# Odoo 19 Views: Basics & Inheritance

## Concept

Views define how records are displayed to the user. They are XML records stored in `ir.ui.view`. Odoo uses a hierarchical view resolution system where a primary view can be extended by multiple extension views.

## Generic Structure

```xml
<record id="view_model_type" model="ir.ui.view">
    <field name="name">model.type</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <field name="name"/>
        </form>
    </field>
</record>
```

## Extension Pattern

**Inheritance (`inherit_id`):**

```xml
<record id="view_model_form_inherit" model="ir.ui.view">
    <field name="name">my.model.form.inherit</field>
    <field name="model">my.model</field>
    <field name="inherit_id" ref="module.original_view_id"/>
    <field name="arch" type="xml">
        <!-- XPath Locator -->
        <xpath expr="//field[@name='description']" position="after">
            <field name="new_field"/>
        </xpath>

        <!-- Field Locator (Shorthand) -->
        <field name="name" position="attributes">
            <attribute name="required">1</attribute>
        </field>
    </field>
</record>
```

## Locator Strategies

- `expr="//field[@name='x']"`: Reliable, standard XPath.
- `field[@name='x']`: Shorthand, finds first occurrence.
- `position`:
  - `inside`: Appends to the end of the element's children.
  - `after` / `before`: Inserts distinct sibling.
  - `replace`: Replaces the element (be careful, this can break other modules).
  - `attributes`: Modifies XML attributes (e.g., `invisible`, `readonly`).

## Common Mistakes

- **Typos in XPath:** Silent failure or massive traceback during upgrade.
- **Replacing Fields:** If you `position="replace"` a field used by the backend logic (or other views), it might crash. Use `invisible="1"` instead.
- **Incorrect Priority:** If multiple views inherit the same parent, `priority` determines order. Default is 16.

## Source Links

- [View Records](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_records.html)
