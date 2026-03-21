/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, xml, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Finance PPM — OKR Dashboard client action.
 *
 * Renders either:
 *   - Power BI embedded report (when ir.config_parameter
 *     `ipai_finance_ppm.powerbi_embed_url` is set)
 *   - Legacy ECharts HTML dashboard (fallback)
 *
 * The Odoo nav bar / breadcrumb remains visible in both modes.
 */
export class OKRDashboard extends Component {
    static template = xml`
        <div class="o_finance_ppm_dashboard" style="height:calc(100vh - 54px);">
            <div t-if="state.loading"
                 style="display:flex;align-items:center;justify-content:center;height:100%;color:#7A8A8C;font-family:monospace;">
                Loading dashboard…
            </div>
            <iframe t-if="!state.loading and state.embedUrl"
                t-att-src="state.embedUrl"
                style="width:100%;height:100%;border:none;display:block;"
                allowfullscreen="true"
                frameborder="0"
            />
            <iframe t-if="!state.loading and !state.embedUrl"
                src="/finance-ppm/okr-dashboard"
                style="width:100%;height:100%;border:none;display:block;"
            />
        </div>
    `;
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, embedUrl: false });

        onWillStart(async () => {
            try {
                const result = await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["ipai_finance_ppm.powerbi_embed_url", false],
                );
                this.state.embedUrl = result || false;
            } catch {
                // Fallback to ECharts if param read fails
                this.state.embedUrl = false;
            }
            this.state.loading = false;
        });
    }
}

registry.category("actions").add("finance_ppm.okr_dashboard", OKRDashboard);
