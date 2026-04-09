---
name: Odoo Web Framework
description: Build web controllers, assets, Owl components, JS modules, registries, services, or client actions. Use when working with Odoo frontend code.
---

# Odoo Web Framework

## Purpose

Write correct Odoo 18 CE web controllers, Owl components, asset bundles, and frontend extensions.

## When to use

- Creating HTTP/JSON controllers
- Building Owl components or widgets
- Registering client actions, field widgets, or systray items
- Managing asset bundles (JS, CSS, SCSS)
- Patching existing frontend behavior
- Working with services and registries

## Inputs or assumptions

- Odoo 18 uses Owl (not legacy widgets) for new components
- No jQuery for new code
- Asset bundles declared in `__manifest__.py`
- `/** @odoo-module **/` required at top of JS files

## Source priority

1. Local JS/XML/SCSS files in `addons/`
2. Odoo 18 CE web framework documentation
3. OCA frontend patterns

## Workflow

1. Create component JS + XML template
2. Register in appropriate registry
3. Add to asset bundle in `__manifest__.py`
4. Test: install module, verify in browser

## Controllers

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route("/my/endpoint", type="json", auth="user", methods=["POST"])
    def my_endpoint(self, **kwargs):
        records = request.env["ipai.my.model"].search([])
        return {"count": len(records)}

    @http.route("/my/page", type="http", auth="public", website=True)
    def my_page(self, **kwargs):
        return request.render("ipai_my_module.my_template", {})
```

| `type` | Use case | Returns |
|--------|----------|---------|
| `json` | API endpoints, AJAX | Dict/list (JSON-RPC) |
| `http` | Web pages, downloads | Response/template |

| `auth` | Access level |
|--------|-------------|
| `none` | No session required |
| `public` | Public user or logged-in |
| `user` | Logged-in users only |

## Owl components

```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class MyWidget extends Component {
    static template = "ipai_my_module.MyWidget";
    static props = { record: Object };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    async onButtonClick() {
        await this.orm.call("ipai.my.model", "action_confirm", [this.props.record.id]);
        this.notification.add("Confirmed!", { type: "success" });
    }
}

registry.category("view_widgets").add("my_widget", {
    component: MyWidget,
});
```

## Asset bundles

In `__manifest__.py`:

```python
"assets": {
    "web.assets_backend": [
        "ipai_my_module/static/src/**/*.js",
        "ipai_my_module/static/src/**/*.xml",
        "ipai_my_module/static/src/**/*.scss",
    ],
},
```

| Bundle | Loaded in |
|--------|-----------|
| `web.assets_backend` | Backend (admin UI) |
| `web.assets_frontend` | Frontend (website/portal) |
| `web.assets_common` | Both backend and frontend |

## Registries

| Registry | Purpose |
|----------|---------|
| `services` | Background services (RPC, notification, user) |
| `actions` | Client actions |
| `fields` | Field widget components |
| `view_widgets` | View-level widget components |
| `systray` | Systray menu items |
| `main_components` | Top-level layout components |

## Patching

```javascript
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async onRecordSaved(record) {
        await super.onRecordSaved(record);
        // custom post-save logic
    },
});
```

## Output format

JS module + XML template + manifest asset entry.

## Verification

- Module installs without JS console errors
- Component renders in expected location
- Asset bundle loads in browser dev tools

## Anti-patterns

- Using jQuery for new code
- Importing from Enterprise asset bundles
- Creating global side effects outside module registration
- Hardcoding URLs in JavaScript (use controllers or `session.origin`)
- Using inline `<script>` tags in QWeb templates
- Missing `/** @odoo-module **/` header
