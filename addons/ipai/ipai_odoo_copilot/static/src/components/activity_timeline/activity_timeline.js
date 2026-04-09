/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * ActivityTimeline — renders structured activity events for the Pulser
 * copilot chat panel.
 *
 * Shows a vertical timeline of operational steps (classify, search,
 * query, respond) with animated status indicators. Never exposes raw
 * chain-of-thought or model reasoning.
 *
 * Props:
 *   activities: Array of {id, label, status, ts?, meta?}
 *   Status values: "pending" | "active" | "done" | "error" | "blocked"
 */
export class ActivityTimeline extends Component {
    static template = "ipai_odoo_copilot.ActivityTimeline";
    static props = {
        activities: { type: Array, optional: true },
    };

    get items() {
        // Only show activities that have started (not pending)
        return (this.props.activities || []).filter(
            (a) => a.status !== "pending"
        );
    }

    get hasActive() {
        return (this.props.activities || []).some(
            (a) => a.status === "active"
        );
    }
}
