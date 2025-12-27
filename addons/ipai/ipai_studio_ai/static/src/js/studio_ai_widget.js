/** @odoo-module **/

/**
 * IPAI Studio AI Widget
 *
 * Provides client-side integration for Studio AI features.
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Studio AI Command Input Widget
 *
 * A form widget that provides command suggestions and validation.
 */
export class StudioAICommandWidget extends Component {
    static template = "ipai_studio_ai.CommandWidget";
    static props = {
        value: { type: String, optional: true },
        readonly: { type: Boolean, optional: true },
        onChange: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({
            value: this.props.value || "",
            suggestions: [],
            showSuggestions: false,
        });

        this.exampleCommands = [
            "Add a phone number field to contacts",
            "Create a status dropdown on sales orders",
            "When an invoice is confirmed, send an email",
            "Add a notes field to the task form",
            "Create a checkbox called 'Approved' on expenses",
        ];
    }

    onInput(ev) {
        this.state.value = ev.target.value;
        this.updateSuggestions();
        if (this.props.onChange) {
            this.props.onChange(ev.target.value);
        }
    }

    onFocus() {
        if (!this.state.value) {
            this.state.suggestions = this.exampleCommands;
            this.state.showSuggestions = true;
        }
    }

    onBlur() {
        // Delay hiding to allow click on suggestion
        setTimeout(() => {
            this.state.showSuggestions = false;
        }, 200);
    }

    selectSuggestion(suggestion) {
        this.state.value = suggestion;
        this.state.showSuggestions = false;
        if (this.props.onChange) {
            this.props.onChange(suggestion);
        }
    }

    updateSuggestions() {
        const query = this.state.value.toLowerCase();
        if (!query) {
            this.state.suggestions = this.exampleCommands;
        } else {
            this.state.suggestions = this.exampleCommands.filter(
                cmd => cmd.toLowerCase().includes(query)
            );
        }
        this.state.showSuggestions = this.state.suggestions.length > 0;
    }
}

// Register the widget
registry.category("fields").add("studio_ai_command", StudioAICommandWidget);

/**
 * Studio AI Quick Action
 *
 * Adds a quick action button to open Studio AI from anywhere.
 */
export class StudioAIQuickAction extends Component {
    static template = "ipai_studio_ai.QuickAction";

    setup() {
        this.action = useService("action");
    }

    async openStudioAI() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Studio AI",
            res_model: "ipai.studio.ai.wizard",
            view_mode: "form",
            target: "new",
        });
    }
}

// Register systray item (optional)
// registry.category("systray").add("ipai_studio_ai.QuickAction", {
//     Component: StudioAIQuickAction,
// });

/**
 * Utility functions for Studio AI
 */
export const StudioAIUtils = {
    /**
     * Detect field type from natural language
     */
    detectFieldType(text) {
        const patterns = {
            monetary: /\b(price|cost|amount|money|currency|budget)\b/i,
            date: /\b(date|day|when|birthday|deadline)\b/i,
            datetime: /\b(datetime|timestamp)\b/i,
            boolean: /\b(checkbox|yes.?no|flag|toggle)\b/i,
            selection: /\b(dropdown|select|choice|status|type)\b/i,
            text: /\b(notes|comments|description|memo)\b/i,
            integer: /\b(integer|count|quantity|number\s+of)\b/i,
            float: /\b(decimal|rate|percentage)\b/i,
            binary: /\b(file|upload|image|photo|document)\b/i,
        };

        for (const [type, pattern] of Object.entries(patterns)) {
            if (pattern.test(text)) {
                return type;
            }
        }
        return "char";
    },

    /**
     * Detect model from natural language
     */
    detectModel(text) {
        const patterns = {
            "res.partner": /\b(contact|customer|vendor|partner)\b/i,
            "sale.order": /\b(sale|sales?\s*order|quotation)\b/i,
            "purchase.order": /\b(purchase|purchase\s*order)\b/i,
            "account.move": /\b(invoice|bill|journal)\b/i,
            "project.task": /\b(task|todo|ticket)\b/i,
            "project.project": /\b(project)\b/i,
            "hr.employee": /\b(employee|staff)\b/i,
            "product.product": /\b(product|item)\b/i,
        };

        for (const [model, pattern] of Object.entries(patterns)) {
            if (pattern.test(text)) {
                return model;
            }
        }
        return null;
    },

    /**
     * Generate technical name from label
     */
    toTechnicalName(label) {
        return "x_" + label
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "_")
            .replace(/^_+|_+$/g, "");
    },
};
