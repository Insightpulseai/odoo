# JS Framework: OWL Components, Registry, Assets

## What it is

OWL (Odoo Web Library) is the modern JS framework used for the Odoo web client (v19+).

## Key concepts

- **Components:** Hierarchical UI building blocks (similar to React/Vue).
- **Registry:** Global store where components, fields, and services are registered.
- **Assets:** JS/CSS bundles loaded by the client.

## Implementation patterns

### Define a Component

```javascript
/** @odoo-module **/
import { Component, xml } from "@odoo/owl";

class MyComponent extends Component {
  static template = xml`<div>Hello <t t-esc="props.name"/></div>`;
}
```

### Register to Actions

```javascript
import { registry } from "@web/core/registry";
registry.category("actions").add("my_client_action", MyComponent);
```

## Gotchas

- **Assets:** Must be declared in `__manifest__.py` under `assets` -> `web.assets_backend`.
- **Hooks:** `onWillStart`, `onMounted` are async-aware lifecycle hooks.

## References

- [Odoo OWL Documentation](https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html)
