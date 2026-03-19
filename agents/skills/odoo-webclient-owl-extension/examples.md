# Examples — odoo-webclient-owl-extension

## Example 1: Systray status indicator

**Input**: Add a systray item showing module health status

**Output** — static/src/js/health_systray.js:
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class HealthSystray extends Component {
    static template = "ipai_health.HealthSystray";
    static props = {};

    setup() {
        this.state = { status: "ok" };
    }

    get statusClass() {
        return `o_ipai_health_indicator o_ipai_health_${this.state.status}`;
    }
}

registry.category("systray").add("ipai_health.HealthSystray", {
    Component: HealthSystray,
    isDisplayed: (env) => true,
});
```

**Output** — static/src/xml/health_systray.xml:
```xml
<?xml version="1.0" encoding="utf-8"?>
<templates xml:space="preserve">
    <t t-name="ipai_health.HealthSystray">
        <div t-att-class="statusClass" title="System Health">
            <i class="fa fa-heartbeat"/>
        </div>
    </t>
</templates>
```

- Asset bundle: web.assets_backend
- Browser test: PASS (no console errors)

## Example 2: Rejected — global Composer patch

**Input**: Patch the mail Composer globally to add AI suggestions

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Global Composer/mail patches caused the `ipai_ai_widget` deprecation (View types not defined form error)
- Recommendation: Use a scoped approach — extend only the specific view or use Odoo 19 native Ask AI patterns

## Example 3: SCSS with incorrect class naming

**Input**: SCSS file uses bare class `.sidebar-panel` without prefix

**Output**:
- Validation: FAIL
- Reason: CSS class `sidebar-panel` does not use `o_<module>_` prefix
- Recommendation: Rename to `.o_ipai_sidebar_panel`
