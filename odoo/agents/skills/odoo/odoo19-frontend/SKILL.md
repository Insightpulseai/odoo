---
name: odoo19-frontend
description: Odoo 19 frontend framework — SPA architecture, registries, services, hooks, patching, domains, translation, field widgets
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/frontend/framework_overview.rst, services.rst, hooks.rst, registries.rst, patching_code.rst, javascript_reference.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Frontend Framework

## SPA Architecture

The Odoo web client is a **single-page application** (SPA) built on the **OWL** component framework. It lives at `/web` and never performs full page reloads -- it fetches only what is needed and updates the UI in place while keeping the URL in sync.

### WebClient Template Structure

```xml
<t t-name="web.WebClient">
    <body class="o_web_client">
        <NavBar/>
        <ActionContainer/>
        <MainComponentsContainer/>
    </body>
</t>
```

- **NavBar**: top navigation bar with menus, systray items, user menu.
- **ActionContainer**: higher-order component displaying the current action controller (client action or a view for `act_window` actions). The action service keeps a stack of active actions (breadcrumbs) and coordinates transitions.
- **MainComponentsContainer**: renders all components registered in the `main_components` registry. This is the primary extension point for adding top-level UI elements.

### Code Structure (`web/static/src`)

| Folder | Contents |
|--------|----------|
| `core/` | Low-level framework (registry, utils, hooks, browser, domain, py_js) |
| `fields/` | All field components |
| `views/` | View components (form, list, kanban, etc.) |
| `search/` | Control panel, search bar, search panel |
| `webclient/` | Web client specific: navbar, user menu, action service |

Import convention -- everything under `web/static/src` uses the `@web` prefix:

```javascript
import { memoize } from "@web/core/utils/functions";
```

---

## Environment Object

Every OWL component can access the shared environment via `this.env`. Odoo enriches it with:

| Key | Value |
|-----|-------|
| `qweb` | All loaded templates (required by OWL) |
| `bus` | Main event bus for global coordination |
| `services` | All deployed services (use `useService` hook instead of direct access) |
| `debug` | String. Non-empty = debug mode active. May contain `"assets"`, `"tests"` |
| `_t` | Translation function |
| `isSmall` | Boolean. `true` when screen width <= 767px (mobile mode) |

```javascript
// Translate a string inside a component
const someString = this.env._t("some text");
```

---

## Bus Events

The environment bus (`env.bus`) is an OWL `EventBus` used for global coordination:

```javascript
env.bus.on("WEB_CLIENT_READY", null, doSomething);
```

### Available Bus Events

| Event | Payload | Trigger |
|-------|---------|---------|
| `ACTION_MANAGER:UI-UPDATED` | mode string (`"current"`, `"new"`, `"fullscreen"`) | Action rendering complete |
| `ACTION_MANAGER:UPDATE` | next rendering info | Action manager computed next interface |
| `MENUS:APP-CHANGED` | none | Menu service current app changed |
| `ROUTE_CHANGE` | none | URL hash changed |
| `RPC:REQUEST` | rpc id | RPC request started |
| `RPC:RESPONSE` | rpc id | RPC request completed |
| `WEB_CLIENT_READY` | none | Web client mounted |
| `FOCUS-VIEW` | none | Main view should focus itself |
| `CLEAR-CACHES` | none | All internal caches should be cleared |
| `CLEAR-UNCOMMITTED-CHANGES` | list of functions | Views with uncommitted changes should clear them |

---

## Registries

Registries are **ordered key/value maps** -- the main extension points of the web client. Import the root registry and use `.category()` for sub-registries:

```javascript
import { Registry } from "@web/core/registry";
import { registry } from "@web/core/registry";

const fieldRegistry = registry.category("fields");
const serviceRegistry = registry.category("services");
const viewRegistry = registry.category("views");
```

### Registry API

```javascript
const myRegistry = new Registry();

// Add entry (throws if key exists unless force:true)
myRegistry.add("hello", "odoo");
myRegistry.add("hello", "odoo2", { force: true });

// Add with ordering
myRegistry.add("item", value, { sequence: 10 });

// Get
myRegistry.get("hello");                   // "odoo2"
myRegistry.get("missing", "default_val");  // "default_val"

// Check existence
myRegistry.contains("hello");  // true

// Get all values (ordered by sequence)
myRegistry.getAll();

// Remove
myRegistry.remove("hello");

// Sub-registry (created on the fly if needed)
const sub = myRegistry.category("sub_name");

// Listen for changes
myRegistry.addEventListener("UPDATE", () => { /* ... */ });
```

### Key Registry Categories

#### Field Registry (`fields`)

Register field widgets for use in views:

```javascript
import { registry } from "@web/core/registry";

class PadField extends Component { /* ... */ }

registry.category("fields").add("pad", {
    component: PadField,
    supportedTypes: ["char"],
});
```

#### View Registry (`views`)

Contains all JS view definitions known to the web client.

#### Action Registry (`actions`)

Client actions -- either a function (called when action is invoked) or an OWL component:

```javascript
registry.category("actions").add("my-custom-action", MyClientActionComponent);
```

#### Service Registry (`services`)

All services activated at startup:

```javascript
registry.category("services").add("myService", {
    dependencies: ["notification"],
    start(env, { notification }) {
        // ...
    }
});
```

#### Systray Registry (`systray`)

Components displayed in the navbar systray zone (right side). Each entry:

```javascript
registry.category("systray").add("myaddon.myItem", {
    Component: MySystrayItem,
    props: {},                          // optional
    isDisplayed: (env) => true,         // optional filter
}, { sequence: 43 });  // default: 50, lower = more right
```

Root element of systray components should be `<li>`.

#### Main Components Registry (`main_components`)

Top-level components rendered by `MainComponentsContainer`:

```javascript
registry.category("main_components").add("LoadingIndicator", {
    Component: LoadingIndicator,
    props: {},  // optional
});
```

#### Formatter Registry (`formatters`)

Functions to format values (typically field values):

```javascript
// format(value, options) => string
```

#### Parser Registry (`parsers`)

Functions to parse string values back into typed values:

```javascript
// parse(string, options) => T (throws on invalid input)
```

#### User Menu Registry (`user_menuitems`)

Items in the user dropdown (top right):

```javascript
registry.category("user_menuitems").add("my item", (env) => ({
    description: env._t("Technical Settings"),
    callback: () => { env.services.action_manager.doAction(3); },
    hide: false,
    sequence: 100,
}));
```

#### Effects Registry (`effects`)

Visual effects like rainbow man. See Effect service below.

---

## Services

Services are **long-lived DI singletons** started at web client boot. They provide features to components (via `useService`) and to other services.

### Defining a Service

```javascript
import { registry } from "@web/core/registry";

const myService = {
    dependencies: ["notification"],  // other services needed
    async: true,                     // mark async methods as safe for destroyed components

    start(env, { notification }) {
        // Return the service's public API (or nothing)
        return {
            doSomething() {
                notification.add("Hello!");
            }
        };
    }
};

registry.category("services").add("myService", myService);
```

### Using a Service in a Component

```javascript
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
    }
}
```

### Cookie Service

Technical name: `cookie`. No dependencies.

```javascript
const cookieService = useService("cookie");

cookieService.current;                      // Object of all cookies
cookieService.setCookie("hello", "odoo");   // Set cookie (default TTL: 1 year)
cookieService.setCookie("hello", "odoo", 3600);  // TTL in seconds
cookieService.deleteCookie("hello");
```

### Effect Service

Technical name: `effect`. No dependencies.

```javascript
const effectService = useService("effect");

// Rainbow man (default effect)
effectService.add({
    type: "rainbow_man",
    message: "Boom! Team record for the past 30 days.",
});

// Rainbow man options:
// params.message: string (default "Well Done!")
// params.messageIsHtml: boolean (default false)
// params.img_url: string (default /web/static/img/smile.svg)
// params.fadeout: "slow"|"medium"|"fast"|"no" (default "medium")
// params.Component: owl.Component (replaces message)
// params.props: object (props for Component)
```

Register custom effects:

```javascript
import { registry } from "@web/core/registry";
import { Component, xml } from "@odoo/owl";

class SepiaEffect extends Component {
    static template = xml`
        <div style="position:absolute;left:0;top:0;width:100%;height:100%;
                     pointer-events:none;background:rgba(124,87,0,0.4);"></div>
    `;
}

function sepiaEffectProvider(env, params = {}) {
    return { Component: SepiaEffect };
}

registry.category("effects").add("sepia", sepiaEffectProvider);
```

### HTTP Service

Technical name: `http`. No dependencies.

```javascript
const httpService = useService("http");

// GET request
const data = await httpService.get("https://example.com/api", "json");
// readMethod options: "text", "json", "formData", "blob", "arrayBuffer"

// POST request
await httpService.post("https://example.com/api", {
    title: "new title",
    content: "new content"
}, "json");
```

### Notification Service

Technical name: `notification`. No dependencies.

```javascript
const notificationService = useService("notification");

// Simple notification
notificationService.add("I'm a simple notification");

// Full-featured notification
const close = notificationService.add("You closed a deal!", {
    title: "Congrats",
    type: "success",       // "info" | "success" | "warning" | "danger"
    sticky: false,         // stays until dismissed
    className: "",         // extra CSS class
    autocloseDelay: 3000,  // milliseconds
    onClose: () => {},     // callback when closed
    buttons: [
        {
            name: "See your Commission",
            primary: true,
            onClick: () => {
                this.actionService.doAction("commission_action");
            },
        },
    ],
});

// Programmatic close
setTimeout(close, 1000);
```

### Router Service

Technical name: `router`. No dependencies.

```javascript
const router = useService("router");

// Read current route
// URL: /web?debug=assets#action=123&owl&menu_id=174
const { pathname, search, hash } = router.current;
// pathname = "/web"
// search = { debug: "assets" }
// hash = { action: 123, owl: "", menu_id: 174 }

// Update URL hash (does not reload page)
router.pushState({ menu_id: 321 });          // merge into existing hash
router.pushState({ yipyip: "" }, true);       // replace hash entirely

// Redirect (reloads page)
router.redirect("/some/url");
router.redirect("/some/url", true);  // wait for server ready
```

Emits `ROUTE_CHANGE` on the main bus when the URL changes.

### RPC Service

Technical name: `rpc`. No dependencies. Low-level -- prefer ORM service for model calls.

```javascript
import { rpc } from "@web/core/network/rpc";

// Call a controller
const result = await rpc("/my/route", { some: "value" });

// With settings
const result = await rpc("/my/route", params, {
    silent: true,  // no loading indicator
    xhr: myXHR,    // custom XMLHttpRequest
});
```

All requests use POST with `application/json`. Errors trigger `RPC_ERROR` on the bus.

### ORM Service

The recommended way to interact with models:

```javascript
const orm = useService("orm");

await orm.call("some.model", "some_method", [arg1, arg2]);
await orm.read("res.partner", [1, 2, 3], ["name", "email"]);
await orm.searchRead("res.partner", [["is_company", "=", true]], ["name"]);
```

### Scroller Service

Technical name: `scroller`. No dependencies. Automatically handles clicks on anchor elements. Emits `SCROLLER:ANCHOR_LINK_CLICKED` on the main bus.

### Title Service

Technical name: `title`. No dependencies.

```javascript
const titleService = useService("title");

// Read current title
titleService.current;  // "Odoo - Import"

// Set title parts (combined with " - " separator)
titleService.setParts({ odoo: "Odoo 19", fruit: "Apple" });
// title = "Odoo 19 - Apple"

// Remove a part
titleService.setParts({ fruit: null });
// title = "Odoo 19"

// Read parts
titleService.getParts();  // { odoo: "Odoo 19" }
```

### User Service

Technical name: `user`. Dependencies: `rpc`.

```javascript
const user = useService("user");

user.context;         // { allowed_company_ids, lang, tz }
user.db;              // database info
user.home_action_id;  // number | false
user.isAdmin;         // boolean (group_erp_manager or superuser)
user.isSystem;        // boolean (group_system)
user.lang;            // "en_US"
user.name;            // "John Doe"
user.partnerId;       // number
user.tz;              // "Europe/Brussels"
user.userId;          // number
user.userName;        // alternative nickname

// Update context
user.updateContext({ isFriend: true });
user.removeFromContext("isFriend");

// Check group membership
const isInSales = await user.hasGroup("sale.group_sales");
```

---

## Hooks

Odoo provides custom hooks built on OWL's hook system.

### useAssets

Location: `@web/core/assets`

Load assets lazily. See the Assets skill for details.

### useAutofocus

Location: `@web/core/utils/hooks`

Automatically focuses an element with `t-ref="autofocus"` when it appears in the DOM:

```javascript
import { useAutofocus } from "@web/core/utils/hooks";

class Comp extends Component {
    static template = "Comp";
    setup() {
        this.inputRef = useAutofocus();
    }
}
```

```xml
<t t-name="Comp">
    <input t-ref="autofocus" type="text"/>
</t>
```

### useBus

Location: `@web/core/utils/hooks`

Subscribe to a bus event, automatically cleaned up on unmount:

```javascript
import { useBus } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        useBus(this.env.bus, "some-event", (event) => {
            console.log(event);
        });
    }
}
```

### usePager

Location: `@web/search/pager_hook`

Display the Pager in the control panel of a view:

```javascript
import { usePager } from "@web/search/pager_hook";

class CustomView extends Component {
    setup() {
        const state = useState({
            offset: 0,
            limit: 80,
            total: 50,
        });

        usePager(() => ({
            offset: state.offset,
            limit: state.limit,
            total: state.total,
            onUpdate: (newState) => {
                Object.assign(state, newState);
            },
        }));
    }
}
```

### usePosition

Location: `@web/core/position_hook`

Position an HTMLElement (popper) relative to another (reference):

```javascript
import { usePosition } from "@web/core/position_hook";
import { Component, xml, useRef } from "@odoo/owl";

class DropMenu extends Component {
    static template = xml`
        <button t-ref="toggler">Toggle</button>
        <div t-ref="menu">
            <t t-slot="default">Default content</t>
        </div>
    `;

    setup() {
        const toggler = useRef("toggler");
        usePosition(
            () => toggler.el,
            {
                popper: "menu",           // t-ref name (default: "popper")
                position: "right-start",  // Direction[-Variant]
                margin: 4,               // pixels between popper and reference
                container: document.documentElement,  // overflow boundary
                onPositioned: (el, { direction, variant, top, left }) => {
                    el.classList.add(`dm-${direction}`);
                },
            },
        );
    }
}
```

**Position values**: `Direction` = `top|bottom|right|left`, `Variant` = `start|middle|end|fit`. Examples: `bottom-start`, `right-end`, `left`, `top-fit`.

### useSpellCheck

Location: `@web/core/utils/hooks`

Enable spellcheck on focus for inputs/textareas/contenteditable elements:

```javascript
import { useSpellCheck } from "@web/core/utils/hooks";

class Comp extends Component {
    static template = "Comp";
    setup() {
        this.simpleRef = useSpellCheck();                       // t-ref="spellcheck"
        this.customRef = useSpellCheck({ refName: "custom" });  // t-ref="custom"
        this.nodeRef = useSpellCheck({ refName: "container" }); // scans children
    }
}
```

```xml
<t t-name="Comp">
    <input t-ref="spellcheck" type="text"/>
    <textarea t-ref="custom"/>
    <div t-ref="container">
        <input type="text" spellcheck="false"/>
        <div contenteditable="true"/>
    </div>
</t>
```

---

## Patching Code

The `patch` function modifies objects/classes in place. Useful when registries alone are insufficient.

### Import

```javascript
import { patch } from "@web/core/utils/patch";
```

### Patching a Simple Object

```javascript
const object = {
    field: "a field",
    fn() {
        // original behavior
    },
};

// Patch with access to parent via super
patch(object, {
    fn() {
        super.fn(...arguments);
        // additional behavior
    },
});
```

### Patching Getters/Setters

```javascript
patch(object, {
    get number() {
        return super.number / 2;
    },
    set number(value) {
        super.number = value;
    },
});
```

### Patching a Class

Patch prototype for instance methods, class itself for static:

```javascript
class MyClass {
    static myStaticFn() { /* ... */ }
    myPrototypeFn() { /* ... */ }
}

// Static methods -- patch the class directly
patch(MyClass, {
    myStaticFn() { /* ... */ },
});

// Instance methods -- patch the prototype
patch(MyClass.prototype, {
    myPrototypeFn() {
        super.myPrototypeFn(...arguments);
        // additional behavior
    },
});
```

### Patching a Component

Components should use `setup()` (not constructors) so they can be patched:

```javascript
patch(MyComponent.prototype, {
    setup() {
        super.setup(...arguments);
        useMyCustomHook();
    },
});
```

### Constructor Workaround

Constructors cannot be patched directly. Use `setup()` pattern:

```javascript
class MyClass {
    constructor() {
        this.setup();
    }
    setup() {
        this.number = 1;
    }
}

patch(MyClass.prototype, {
    setup() {
        super.setup(...arguments);
        this.doubleNumber = this.number * 2;
    },
});
```

### Removing a Patch

```javascript
const unpatch = patch(object, { /* ... */ });
// later (typically in test teardown)
unpatch();
```

### Patching Multiple Objects with Same Logic

The `super` keyword binds to the extension object, so create fresh objects:

```javascript
function createExtensionObj() {
    return {
        method() {
            super.method();
            doCommonThings();
        },
    };
}

patch(obj1, createExtensionObj());
patch(obj2, createExtensionObj());
```

**Warning**: Never spread (`...ext`) an extension into another -- `super` references break.

---

## Domain Class

Domains represent sets of records matching conditions. The `Domain` class handles both list and string representations:

```javascript
import { Domain } from "@web/core/domain";

// From list of conditions
new Domain([["a", "=", 3]]).contains({ a: 3 });  // true

const domain = new Domain(["&", "&", ["a", "=", 1], ["b", "=", 2], ["c", "=", 3]]);
domain.contains({ a: 1, b: 2, c: 3 });  // true
domain.contains({ a: -1, b: 2, c: 3 }); // false

// Convert to string
domain.toString();

// Evaluate string domain with context
new Domain("[('a', '>', b)]").toList({ b: 3 }); // [['a', '>', 3]]

// Static combinators
Domain.and([[["a", "=", 1]], "[('uid', '<=', uid)]"]).toString();
// ["&", ("a", "=", 1), ("uid", "<=", uid)]

Domain.or([[["a", "=", 1]], "[('uid', '<=', uid)]"]).toString();
// ["|", ("a", "=", 1), ("uid", "<=", uid)]

Domain.not([["a", "=", 1]]).toString();
// ["!", ("a", "=", 1)]

Domain.combine([[["a", "=", 1]], "[('uid', '<=', uid)]"], "AND").toString();
```

---

## Python Interpreter (evaluateExpr)

Built-in small Python expression evaluator for view modifiers and domains:

```javascript
import { evaluateExpr } from "@web/core/py_js/py";

evaluateExpr("1 + 2*{'a': 1}.get('b', 54) + v", { v: 33 }); // 142
```

Available functions:

| Function | Description |
|----------|-------------|
| `tokenize(expr)` | Returns `Token[]` |
| `parse(tokens)` | Returns AST from tokens |
| `parseExpr(expr)` | Returns AST from string |
| `evaluate(ast, context?)` | Evaluates AST to value |
| `evaluateExpr(expr, context?)` | Full pipeline: string to value |

---

## Debug Mode

The `debug` value is a string in `env.debug`:

- **Empty string**: debug mode off
- **Contains `"assets"`**: un-minified JS/CSS, source maps enabled
- **Contains `"tests"`**: `web.assets_tests` bundle injected (test tours)

To conditionally show elements only in debug mode, use the group `base.group_no_one`:

```xml
<field name="fname" groups="base.group_no_one"/>
```

---

## Translation (`_t`)

```javascript
import { _t } from "@web/core/l10n/translation";

// Simple translation
const str = _t("some text");

// Static property (extracted for PO files)
class SomeComponent extends Component {
    static exampleString = _t("this should be translated");
}

// Interpolation with placeholders
const str = _t("Hello %s, you have %s unread messages.", user.name, unreadCount);
```

The string argument must be a **static literal** (no dynamic expressions) because it is extracted for PO file generation.

---

## Browser Object

Mockable wrapper around browser APIs for testability:

```javascript
import { browser } from "@web/core/browser/browser";

browser.setTimeout(someFunction, 1000);
browser.localStorage.getItem("key");
browser.location.href;
```

Available: `addEventListener`, `cancelAnimationFrame`, `clearInterval`, `clearTimeout`, `console`, `Date`, `fetch`, `history`, `localStorage`, `location`, `navigator`, `open`, `random`, `removeEventListener`, `requestAnimationFrame`, `sessionStorage`, `setInterval`, `setTimeout`, `XMLHttpRequest`.

---

## Session

Server-injected data available without an extra roundtrip:

```javascript
import { session } from "@web/session";
const myValue = session.some_key;
```

Extend from Python by overriding `ir.http.session_info()`:

```python
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = ['ir.http']

    def session_info(self):
        result = super().session_info()
        result['some_key'] = get_some_value_from_db()
        return result
```

---

## Context

### User Context

Available through the `user` service. Contains `allowed_company_ids`, `lang`, `tz`. The ORM service auto-appends it to every request.

```javascript
const user = useService("user");
console.log(user.context);  // { allowed_company_ids: [1], lang: "en_US", tz: "Europe/Brussels" }
```

### Action Context

Defined on `ir.actions.act_window` / `ir.actions.client` as a `char` field:

```xml
<field name="context">{'search_default_customer': 1}</field>
```

Extend programmatically:

```javascript
const actionService = useService("action");
actionService.doAction("addon_name.something", {
    additional_context: {
        default_period_id: defaultPeriodId,
    }
});
```

---

## Client Actions

A client action is an OWL component registered in the action registry:

```javascript
import { registry } from "@web/core/registry";

class MyClientAction extends Component {
    static template = "myaddon.MyClientAction";
    // ...
}

registry.category("actions").add("my-custom-action", MyClientAction);
```

Server record:

```xml
<record id="my_client_action" model="ir.actions.client">
    <field name="name">Some Name</field>
    <field name="tag">my-custom-action</field>
</record>
```

---

## Field Widgets Reference

### Decorations

Fields support decoration attributes for conditional text styling:

```xml
<field name="state" decoration-danger="amount &lt; 10000"/>
```

Valid decorations: `decoration-bf`, `decoration-it`, `decoration-danger`, `decoration-info`, `decoration-muted`, `decoration-primary`, `decoration-success`, `decoration-warning`. Each maps to CSS class `text-X`.

### Non-Relational Fields

#### Integer (`integer`)

Supported types: `integer`

```xml
<field name="int_value" options="{'type': 'number', 'step': 100}" />
<field name="int_value" options='{"format": false}' />
```

#### Float (`float`)

Supported types: `float`

```xml
<field name="factor" digits="[42,5]" />
<field name="float_value" options="{'type': 'number', 'step': 0.1}" />
<field name="float_value" options="{'format': false}" />
<field name="float_value" options="{'min_display_digits': 3}" />
<field name="float_value" options="{'hide_trailing_zeros': true}" />
```

#### Float Time (`float_time`)

Displays float as time (0.5 = "0:30", 4.75 = "4:45"). Supported types: `float`.

#### Float Factor (`float_factor`)

Displays float converted by a factor. Supported types: `float`.

#### Float Toggle (`float_toggle`)

Button cycling through predefined values:

```xml
<field name="days_to_close" widget="float_toggle" options="{'factor': 2, 'range': [0, 4, 8]}" />
```

#### Boolean (`boolean`)

Default for `boolean` fields.

#### Boolean Favorite (`boolean_favorite`)

Star toggle, works in readonly mode too. Supported types: `boolean`.

#### Boolean Toggle (`boolean_toggle`)

Toggle switch display. Supported types: `boolean`.

#### Char (`char`)

Default for `char` fields.

#### Text (`text`)

Default for `text` fields.

#### Date (`date`)

Supported types: `date`

```xml
<field name="datefield" options="{'min_date': 'today', 'max_date': '2023-12-31'}" />
<field name="datefield" options="{'warn_future': true}" />
<field name="datefield" options="{'numeric': true}" />
```

#### DateTime (`datetime`)

Supported types: `datetime`

```xml
<field name="datetimefield" options="{'rounding': 10}" />
<field name="datetimefield" widget="datetime" options="{'show_seconds': true}" />
<field name="datetimefield" widget="datetime" options="{'show_time': false}" />
<field name="datetimefield" widget="datetime" options="{'show_date': false}" />
```

#### Date Range (`daterange`)

Supported types: `date`, `datetime`

```xml
<field name="start_date" widget="daterange" options="{'end_date_field': 'end_date'}" />
<field name="end_date" widget="daterange" options="{'start_date_field': 'start_date'}" />
```

#### Remaining Days (`remaining_days`)

Displays delta in days from today. Supported types: `date`, `datetime`.

#### Monetary (`monetary`)

Supported types: `monetary`, `float`

```xml
<field name="value" widget="monetary" options="{'currency_field': 'currency_id'}" />
<field name="value" widget="monetary" options="{'hide_trailing_zeros': true}" />
```

#### Email (`email`)

Renders as clickable `mailto:` link in readonly. Supported types: `char`.

#### Phone (`phone`)

Renders as clickable `tel:` link on capable devices. Supported types: `char`.

#### URL (`url`)

Renders as clickable link in readonly. Supported types: `char`.

```xml
<field name="foo" widget="url" text="Some URL" />
<!-- options: website_path (boolean, default false) -->
```

#### Domain (`domain`)

Tree-like domain builder with live record preview. Supported types: `char`.

```xml
<!-- options: model, foldable, in_dialog, count_limit -->
```

#### Handle (`handle`)

Drag-and-drop reordering in list views. Supported types: `integer`.

#### Priority (`priority`)

Star-based priority selector (works in readonly). Supported types: `selection`.

#### Image (`image`)

Supported types: `binary`

```xml
<field name="image" widget="image" options="{'preview_image': 'image_128'}" />
```

#### Binary (`binary`)

Upload/download binary files. Supported types: `binary`.

```xml
<field name="datas" filename="datas_fname" />
```

#### Badge (`badge`)

Bootstrap badge pill. Supported types: `char`, `selection`, `many2one`.

```xml
<field name="foo" widget="badge" decoration-danger="state == 'cancel'" />
```

#### Progress Bar (`progressbar`)

```xml
<field name="absence" widget="progressbar"
    options="{'current_value': 'absence_of_today', 'max_value': 'total_employee', 'editable': false}" />
```

#### Ace Editor (`ace`)

Code editor for XML/Python. Supported types: `char`, `text`.

#### Stat Info (`statinfo`)

For stat buttons. Supported types: `integer`, `float`.

#### Percent Pie (`percentpie`)

Pie chart (0-100). Supported types: `integer`, `float`.

### Relational Fields

#### Selection (`selection`)

```xml
<field name="tax_id" widget="selection" placeholder="Select a tax" />
```

#### Radio (`radio`)

```xml
<field name="type_id" widget="radio" options="{'horizontal': true}" />
```

#### Selection Badge (`selection_badge`)

Rectangular badge selector. Supported types: `selection`, `many2one`.

#### Many2one (`many2one`)

```xml
<field name="currency_id" options="{'no_create': true, 'no_open': true}" />
<!-- Options: quick_create, no_create, no_quick_create, no_create_edit,
     create_name_field, always_reload, no_open -->
<!-- Attributes: can_create, can_write -->
```

#### Many2one Avatar (`many2one_avatar`)

Displays image from `image.mixin` model next to display_name.

#### Many2one Avatar User (`many2one_avatar_user`)

Avatar with chat on click. Points to `res.users`.

#### Many2many (`many2many`)

```xml
<field name="tag_ids" options="{'create_text': 'Add a tag', 'link': true, 'unlink': true}" />
```

#### Many2many Tags (`many2many_tags`)

```xml
<field name="category_id" widget="many2many_tags"
    options="{'color_field': 'color', 'no_edit_color': true, 'edit_tags': true}" />
```

#### Many2many Checkboxes (`many2many_checkboxes`)

Checkbox list (max 100 items displayed).

#### Many2many Binary (`many2many_binary`)

Multi-file upload for `ir.attachment`.

#### One2many (`one2many`)

```xml
<field name="line_ids" options="{'create': true, 'delete': true, 'create_text': 'Add line'}" />
```

#### Status Bar (`statusbar`)

Form view flow bar. Supported types: `selection`, `many2one`.

#### Reference (`reference`)

Model selector + many2one. Supported types: `char`, `reference`.

### View Widgets

#### Ribbon (`web_ribbon`)

```xml
<widget name="web_ribbon" title="Archived" bg_color="text-bg-danger"/>
```

#### Week Days (`week_days`)

```xml
<widget name="week_days" />
```

---

## Notifications from Python

Trigger notifications from server-side code:

```python
def show_notification(self):
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _('Success'),
            'message': _('Your signature request has been sent.'),
            'sticky': False,
            'type': 'success',  # info, success, warning, danger
        }
    }
```
