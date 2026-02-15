# Odoo 19 QWeb Templates

## Concept

QWeb is the primary XML-based templating engine used by Odoo for both backend reports and frontend web pages. It processes XML directives (prefixed with `t-`) to generate HTML.

## Applies To

- Website Pages/Snippets
- PDF Reports (QWeb PDF)
- Kanban/Card Views (Backend)
- Owl Components (Frontend)

## Core Directives

- `t-out` / `t-esc`: Output data (HTML escaped by default).
- `t-if` / `t-elif` / `t-else`: Conditional rendering.
- `t-foreach="collection" t-as="item"`: Loops.
- `t-att-name="expr"`: Dynamic attribute binding.
- `t-call`: Sub-template inclusion.
- `t-set` / `t-value`: Variable definition.

## Extension Pattern

**Inheriting Templates (XPath):**

```xml
<template id="my_custom_template" inherit_id="base.original_template">
    <xpath expr="//div[@class='header']" position="after">
        <div class="new-banner">Welcome!</div>
    </xpath>
</template>
```

**Calling Sub-templates:**

```xml
<t t-call="module.other_template">
    <t t-set="var_name" t-value="42"/>
</t>
```

## Common Mistakes

- **Escaping:** `t-raw` is deprecated; use `t-out` for general output. For trusted raw HTML, use `Markup` safe strings in Python side.
- **Loop Variables:** Accessing loop metadata (`item_index`, `item_first`) requires strictly adhering to the syntax `${item}_index`.
- **XPath Failures:** Relying on fragile selectors (like `expr="//div[3]"`) that break when the parent changes. Use `name` or `class` attributes or unique IDs.

## Agent Notes

- In Owl components, QWeb is compiled to JS. In Server contexts (Reports), it's interpreted by lxml/Python.
- `<t>` elements disappear in the final DOM; use them to attach logic without polluting the markup.

## Source Links

- [QWeb Templates](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)
