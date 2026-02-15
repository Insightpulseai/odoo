# QWeb Templates

## What it is

QWeb is Odoo's primary templating engine, used for generating HTML (in the web client and website) and XML (for Reports).

## Key concepts

- ** Directives:** Special XML attributes starting with `t-` (e.g., `t-if`, `t-foreach`, `t-esc`, `t-call`).
- **Inheritance:** Templates can inherit and modify other templates using XPath.
- **Context:** Templates have access to variables passed during rendering (e.g., `docs`, `user`).

## Implementation patterns

### Basic Template

```xml
<template id="my_template">
    <div t-foreach="docs" t-as="doc">
        <span t-esc="doc.name"/>
    </div>
</template>
```

### Inheritance (Extension)

```xml
<template id="my_extension" inherit_id="module.original_template">
    <xpath expr="//div[@class='header']" position="after">
        <div class="subheader">New Content</div>
    </xpath>
</template>
```

## Gotchas

- **t-field vs t-esc:** `t-field` handles formatting (currency, date) and is edit-aware in the website editor. `t-esc` outputs raw text (escaped).
- **XPath:** finding elements requires precise path matching. Use unique classes or IDs where possible to make extensions robust.

## References

- [Odoo QWeb Documentation](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)
