/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * DiffPreview - Shows before/after comparison for write actions
 *
 * Schema:
 * {
 *   field_name: { old: "old value", new: "new value" },
 *   another_field: { old: null, new: "new value" }
 * }
 */
export class DiffPreview extends Component {
    static template = "ipai_ask_ai.DiffPreview";
    static props = {
        diff: Object,
        onApply: { type: Function, optional: true },
        onCancel: { type: Function, optional: true },
    };

    get fields() {
        const diff = this.props.diff || {};
        return Object.entries(diff).map(([field, values]) => ({
            field,
            old: values.old,
            new: values.new,
            isAdd: values.old === null || values.old === undefined,
            isRemove: values.new === null || values.new === undefined,
            isChange: values.old !== null && values.old !== undefined &&
                      values.new !== null && values.new !== undefined,
        }));
    }

    /**
     * Format a value for display
     */
    formatValue(value) {
        if (value === null || value === undefined) {
            return "(empty)";
        }
        if (typeof value === "object") {
            return JSON.stringify(value, null, 2);
        }
        return String(value);
    }

    /**
     * Get line class based on change type
     */
    getLineClass(field) {
        if (field.isAdd) return "ipai-diff-line--add";
        if (field.isRemove) return "ipai-diff-line--remove";
        return "ipai-diff-line--change";
    }

    /**
     * Apply the changes
     */
    onApply() {
        if (this.props.onApply) {
            this.props.onApply();
        }
    }

    /**
     * Cancel / close preview
     */
    onCancel() {
        if (this.props.onCancel) {
            this.props.onCancel();
        }
    }
}
