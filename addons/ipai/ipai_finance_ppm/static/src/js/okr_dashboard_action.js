/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, xml, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Finance PPM — Power BI Dashboard client action.
 *
 * Embeds a Power BI report inside the Odoo backend via iframe.
 * Configure the report URL in Settings → Technical → Parameters:
 *   key: ipai_ppm.powerbi_report_url
 *
 * The Odoo nav bar / breadcrumb remains visible.
 */
export class OKRDashboard extends Component {
    static template = xml`
        <div class="o_finance_ppm_dashboard" style="height:calc(100vh - 54px);">
            <div t-if="state.loading"
                 style="display:flex;align-items:center;justify-content:center;height:100%;color:#7A8A8C;font-family:monospace;">
                Loading dashboard…
            </div>
            <iframe t-if="!state.loading and state.reportUrl"
                t-att-src="state.reportUrl"
                style="width:100%;height:100%;border:none;display:block;"
                allowfullscreen="true"
                frameborder="0"
            />
            <div t-if="!state.loading and !state.reportUrl"
                 style="display:flex;align-items:center;justify-content:center;height:100%;color:#7A8A8C;font-family:monospace;flex-direction:column;gap:8px;">
                <span style="font-size:1.2em;">Power BI report not configured</span>
                <span>Set <code>ipai_ppm.powerbi_report_url</code> in Settings → Technical → Parameters</span>
            </div>
        </div>
    `;
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, reportUrl: false });

        onWillStart(async () => {
            try {
                const result = await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["ipai_ppm.powerbi_report_url", false],
                );
                this.state.reportUrl = result || false;
            } catch {
                this.state.reportUrl = false;
            }
            this.state.loading = false;
        });
    }
}

registry.category("actions").add("finance_ppm.okr_dashboard", OKRDashboard);
