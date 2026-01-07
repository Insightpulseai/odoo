/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CommandCenterDashboard extends Component {
    static template = "ipai_command_center.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            stats: {
                runs_today: 0,
                runs_pending: 0,
                runs_failed_24h: 0,
                avg_duration_ms: 0,
                by_type: {},
                by_state: {},
            },
            alerts: {
                critical: 0,
                error: 0,
                warning: 0,
                info: 0,
            },
            recent_runs: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Load run statistics
            const stats = await this.orm.call(
                "ipai.command.center.run",
                "get_dashboard_data",
                []
            );
            this.state.stats = stats;

            // Load alert counts
            const alerts = await this.orm.call(
                "ipai.command.center.alert",
                "get_active_alerts_count",
                []
            );
            this.state.alerts = alerts;

            // Load recent runs
            const runs = await this.orm.searchRead(
                "ipai.command.center.run",
                [],
                ["name", "run_type", "state", "date_start", "duration", "user_id"],
                { limit: 10, order: "date_start desc" }
            );
            this.state.recent_runs = runs;

            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.loading = false;
        }
    }

    async refresh() {
        this.state.loading = true;
        await this.loadDashboardData();
    }

    openRuns() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Runs",
            res_model: "ipai.command.center.run",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    openAlerts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Alerts",
            res_model: "ipai.command.center.alert",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            context: { search_default_active: 1 },
        });
    }

    openFailedRuns() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Failed Runs",
            res_model: "ipai.command.center.run",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            context: { search_default_failed: 1 },
        });
    }

    formatDuration(ms) {
        if (!ms) return "0s";
        const seconds = Math.floor(ms / 1000);
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    }

    getStateClass(state) {
        const classes = {
            pending: "pending",
            running: "running",
            done: "done",
            failed: "failed",
            cancelled: "failed",
        };
        return classes[state] || "pending";
    }

    getStateIcon(state) {
        const icons = {
            pending: "fa-clock-o",
            running: "fa-spinner fa-spin",
            done: "fa-check",
            failed: "fa-times",
            cancelled: "fa-ban",
        };
        return icons[state] || "fa-question";
    }
}

CommandCenterDashboard.props = {};

registry.category("actions").add("ipai_command_center_dashboard", CommandCenterDashboard);
