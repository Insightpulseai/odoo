/** @odoo-module **/
/**
 * Superset Dashboard Embed Component
 *
 * Uses Superset Embedded SDK pattern with guest tokens issued by Odoo.
 * The component fetches a guest token from the Odoo backend, then
 * initializes the Superset embed in an iframe.
 */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SupersetEmbed extends Component {
    static template = "ipai_superset_connector.SupersetEmbed";
    static props = {
        dashboard_id: { type: String },
        dashboard_name: { type: String, optional: true },
        hide_title: { type: Boolean, optional: true },
        hide_filters: { type: Boolean, optional: true },
        hide_charts_controls: { type: Boolean, optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            error: null,
            iframeSrc: null,
            supersetUrl: null,
        });

        this.iframeRef = null;

        onMounted(() => {
            this.loadDashboard();
        });

        onWillUnmount(() => {
            // Cleanup if needed
        });
    }

    async loadDashboard() {
        const dashboardId = this.props.dashboard_id;

        try {
            this.state.loading = true;
            this.state.error = null;

            // Fetch guest token from Odoo backend
            const result = await this.rpc(
                `/ipai/superset/guest_token/${dashboardId}`,
                {}
            );

            if (!result || !result.token) {
                throw new Error("No token received from server");
            }

            this.state.supersetUrl = result.superset_url;

            // Build embed URL with guest token
            // Format: {superset_url}/superset/dashboard/{id}/?standalone=3&guest_token={token}
            const embedParams = new URLSearchParams();
            embedParams.set("standalone", "3"); // Minimal chrome
            embedParams.set("guest_token", result.token);

            if (this.props.hide_title) {
                embedParams.set("hide_title", "true");
            }
            if (this.props.hide_filters) {
                embedParams.set("hide_filter_bar", "true");
            }
            if (this.props.hide_charts_controls) {
                embedParams.set("hide_charts_controls", "true");
            }

            const iframeSrc = `${result.superset_url}/superset/dashboard/${dashboardId}/?${embedParams.toString()}`;
            this.state.iframeSrc = iframeSrc;
            this.state.loading = false;

        } catch (error) {
            console.error("Failed to load Superset dashboard:", error);
            this.state.loading = false;
            this.state.error = error.message || "Failed to load dashboard";
            this.notification.add(
                `Failed to load dashboard: ${error.message}`,
                { type: "danger" }
            );
        }
    }

    onIframeLoad() {
        // Called when iframe finishes loading
        this.state.loading = false;
    }

    onIframeError() {
        this.state.error = "Failed to load Superset iframe";
        this.state.loading = false;
    }

    async refreshToken() {
        // Allow manual refresh if token expires
        await this.loadDashboard();
    }
}

// Register as a client action
registry.category("actions").add("ipai_superset_embed", SupersetEmbed);


/**
 * Dashboard List Component
 *
 * Shows available dashboards for the current user.
 */
export class SupersetDashboardList extends Component {
    static template = "ipai_superset_connector.SupersetDashboardList";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            dashboards: [],
            error: null,
        });

        onMounted(() => {
            this.loadDashboards();
        });
    }

    async loadDashboards() {
        try {
            this.state.loading = true;
            const result = await this.rpc("/ipai/superset/dashboards", {});
            this.state.dashboards = result || [];
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load dashboards:", error);
            this.state.error = error.message;
            this.state.loading = false;
        }
    }

    openDashboard(dashboard) {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "ipai_superset_embed",
            name: dashboard.name,
            params: {
                dashboard_id: String(dashboard.id),
                dashboard_name: dashboard.name,
            },
        });
    }
}

registry.category("actions").add("ipai_superset_dashboard_list", SupersetDashboardList);
