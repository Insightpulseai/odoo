# Odoo 19 Owl Components

## Basic Component

**Path:** `my_module/static/src/components/my_component.js`

```javascript
/** @odoo-module */

import { Component, useState, xml } from "@odoo/owl";

export class MyComponent extends Component {
  static template = "my_module.MyComponent"; // References XML ID

  setup() {
    this.state = useState({ count: 0 });
  }

  increment() {
    this.state.count++;
  }
}
```

**Template:** `my_module/static/src/components/my_component.xml`

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component" t-on-click="increment">
            Counter: <t t-esc="state.count"/>
        </div>
    </t>
</templates>
```

## Standard Components

Odoo provides a suite of reusable components.

- **Dropdown:** `<Dropdown/>`
- **Notebook:** `<Notebook/>` (Tabs)
- **Pager:** `<Pager/>`
- **CheckBox:** `<CheckBox/>`
- **ActionSwiper:** Touch actions.

## Best Practices

- **Setup vs Constructor:** valid Odoo components MUST use `setup()`, NOT `constructor()`.
- **Template Naming:** Always use `addon_name.ComponentName` to avoid collisions.
- **Directives:** Use `t-on-click`, `t-model` (two-way binding), `t-ref` (references).
- **Hooks:** Use `useService`, `useRef`, `onWillStart`, `onMounted` inside `setup()`.

## Source Links

- [Owl Components](https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html)
