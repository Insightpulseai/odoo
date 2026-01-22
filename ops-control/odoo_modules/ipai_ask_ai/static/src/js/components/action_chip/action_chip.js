/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * ActionChip - Clickable action button for AI responses
 *
 * Types:
 * - create: Create new record
 * - update: Update existing record
 * - navigate: Navigate to record/view
 * - search: Perform search
 */
export class ActionChip extends Component {
    static template = "ipai_ask_ai.ActionChip";
    static props = {
        action: Object,
        index: Number,
        expanded: { type: Boolean, optional: true },
        executed: { type: Boolean, optional: true },
        onClick: { type: Function, optional: true },
        onExecute: { type: Function, optional: true },
    };

    get label() {
        return this.props.action.label || this.getDefaultLabel();
    }

    get description() {
        return this.props.action.description || "";
    }

    get type() {
        return this.props.action.type || "navigate";
    }

    get icon() {
        const icons = {
            create: "fa-plus",
            update: "fa-pencil",
            navigate: "fa-arrow-right",
            search: "fa-search",
        };
        return icons[this.type] || "fa-play";
    }

    get chipClass() {
        const classes = ["ipai-action-chip"];

        // Type-based styling
        if (this.type === "create") {
            classes.push("ipai-action-chip--success");
        } else if (this.type === "update") {
            classes.push("ipai-action-chip--warning");
        }

        if (this.props.expanded) {
            classes.push("ipai-action-chip--expanded");
        }

        if (this.props.executed) {
            classes.push("ipai-action-chip--executed");
        }

        return classes.join(" ");
    }

    get hasPreview() {
        return !!this.props.action.preview_diff;
    }

    getDefaultLabel() {
        const labels = {
            create: "Create",
            update: "Update",
            navigate: "Open",
            search: "Search",
        };
        return labels[this.type] || "Execute";
    }

    /**
     * Handle click
     */
    onClick() {
        if (this.props.executed) return;

        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}
