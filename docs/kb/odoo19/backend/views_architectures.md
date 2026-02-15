# Odoo 19 View Architectures

## Form View

**Purpose:** Create/Edit a single record.
**Root:** `<form>`
**Structure:**

```xml
<form>
    <header>
        <!-- Workflow buttons and status bar -->
        <button name="action_confirm" string="Confirm" type="object" class="oe_highlight"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <!-- Title and main content -->
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <group>
            <group>
                <field name="partner_id"/>
            </group>
            <group>
                <field name="date"/>
            </group>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids">
                    <list editable="bottom">
                        <field name="product_id"/>
                        <field name="qty"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <!-- Chatter is traditionally at the bottom, outside sheet -->
    <chatter/>
</form>
```

## List View (Tree)

**Purpose:** Display multiple records.
**Root:** `<list>` (formerly `tree`).
**Attributes:** `editable="top|bottom"`, `multi_edit="1"`.
**Structure:**

```xml
<list decoration-danger="amount &lt; 0">
    <field name="name"/>
    <field name="amount" sum="Total"/>
    <field name="state" widget="badge"/>
</list>
```

## Search View

**Purpose:** Filter and Group By options in the Control Panel.
**Root:** `<search>`
**Structure:**

```xml
<search>
    <field name="name"/>
    <field name="partner_id"/>
    <filter name="my_records" string="My Records" domain="[('user_id', '=', uid)]"/>
    <group expand="1" string="Group By">
        <filter name="groupby_date" context="{'group_by': 'date'}"/>
    </group>
</search>
```

## Kanban View

**Purpose:** Card-based visualization.
**Root:** `<kanban>`
**Structure:**

```xml
<kanban>
    <field name="name"/>
    <field name="color"/>
    <templates>
        <t t-name="card">
            <div class="oe_kanban_global_click">
                <field name="name"/>
            </div>
        </t>
    </templates>
</kanban>
```

## Common Mistakes

- **Invisible Fields:** Fields used in `attrs`, `domain`, or `code` MUST be present in the view. If you don't want to show them, use `<field name="x" invisible="1"/>`.
- **List Editable:** If a list is `editable`, generic form view buttons (like "Edit" in a modal) might behave differently or be unavailable.
- **Search View Defaults:** To apply a filter by default, use `context="{'search_default_my_filter': 1}"` in the Window Action, NOT in the search view itself.

## Source Links

- [View Architectures](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)
