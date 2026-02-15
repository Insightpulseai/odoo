# Odoo 19 Owl Services & Registries

## Services

Services are singleton objects that provide shared functionality across the application.

**Definition:**

```javascript
import { registry } from "@web/core/registry";

export const myService = {
  dependencies: ["rpc", "notification"],
  start(env, { rpc, notification }) {
    let state = 0;
    return {
      increment() {
        state++;
        notification.add("State incremented: " + state);
      },
      getValue: () => state,
    };
  },
};

registry.category("services").add("myService", myService);
```

**Usage (in Components):**

```javascript
import { useService } from "@web/core/utils/hooks";

setup() {
    this.myService = useService("myService");
}
```

## Core Services

- **rpc:** Low-level server requests (`/my/route`).
- **orm:** High-level model interaction (`searchRead`, `create`, `write`).
- **notification:** Show toast messages (`add(message, options)`).
- **action:** Execute window/server actions (`doAction`).
- **user:** User context and info (`context`, `hasGroup`).
- **router:** URL state management.
- **cookie:** Browser cookies.

## Registries

Registries are ordered key-value stores used to extend Odoo's behavior.

**API:**

```javascript
import { registry } from "@web/core/registry";
const myRegistry = registry.category("my_category");

myRegistry.add("item_key", itemValue, { sequence: 10 });
const items = myRegistry.getAll(); // Ordered by sequence
```

**Common Categories:**

- `services`: Global services (as seen above).
- `main_components`: Top-level overlay components (Systray, LoadingIndicator).
- `fields`: Field widgets (e.g., `Char`, `Many2One`).
- `views`: View architectures (e.g., `Form`, `List`).
- `actions`: Action handlers (`ir.actions.client`).
- `formatters` / `parsers`: Data formatting/parsing.

## Agent Notes

- **Service Lifecycle:** Services start _once_ when the web client initializes (or lazily).
- **Dependency Injection:** Always declare dependencies in the `dependencies` array.
- **`env`:** The `env` object is the global context, but prefer `useService` over accessing `env.services` directly in components.

## Source Links

- [Services](https://www.odoo.com/documentation/19.0/developer/reference/frontend/services.html)
- [Registries](https://www.odoo.com/documentation/19.0/developer/reference/frontend/registries.html)
