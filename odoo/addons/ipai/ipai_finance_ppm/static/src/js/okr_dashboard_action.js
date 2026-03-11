/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, xml } from "@odoo/owl";

/**
 * Finance PPM — OKR Dashboard client action.
 * Renders the standalone HTML dashboard inside an iframe so that
 * the full Odoo nav bar / breadcrumb remains visible.
 */
export class OKRDashboard extends Component {
    static template = xml`
        <iframe
            src="/finance-ppm/okr-dashboard"
            style="width:100%;height:calc(100vh - 54px);border:none;display:block;"
        />
    `;
    static props = {};
}

registry.category("actions").add("finance_ppm.okr_dashboard", OKRDashboard);
