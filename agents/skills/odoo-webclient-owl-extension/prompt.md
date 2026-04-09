# Prompt — odoo-webclient-owl-extension

You are extending the Odoo CE 19 web client for the InsightPulse AI platform.

Your job is to:
1. Create or extend an OWL component using Odoo 18 patterns
2. Use `patch()` for extending existing components (never monkey-patch)
3. Create XML templates for component markup
4. Create SCSS styles with `o_<module>_` class prefix
5. Register assets in the correct bundle (web.assets_backend or web.assets_frontend)
6. Test rendering in the browser on a disposable database
7. Verify no JS console errors

Platform context:
- JS files: `static/src/js/` in ipai_* module
- XML templates: `static/src/xml/`
- SCSS: `static/src/scss/`
- Asset registration: `__manifest__.py` under `assets` key

OWL component pattern (Odoo 18):
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "ipai_module.MyComponent";
    static props = { ... };
    setup() {
        // lifecycle hooks here
    }
}
```

Patching existing component:
```javascript
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        // additional setup
    },
});
```

Asset registration in manifest:
```python
'assets': {
    'web.assets_backend': [
        'ipai_module/static/src/js/my_component.js',
        'ipai_module/static/src/xml/my_component.xml',
        'ipai_module/static/src/scss/my_component.scss',
    ],
},
```

Output format:
- Component: name and type (new/extended)
- JS file: path
- XML template: path
- SCSS: path (if applicable)
- Asset bundle: which bundle registered in
- Browser test: pass/fail (no console errors)
- Evidence: screenshot or console log

Rules:
- CSS class prefix: o_<module>_ (e.g. o_ipai_copilot_panel)
- SCSS variables: $o-* prefix
- No bare CSS class names or ID selectors
- No !important except overriding Odoo core
- Use patch() for extensions, never monkey-patch
- Never create global Composer/mail patches
- Register in correct asset bundle
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
