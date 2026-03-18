/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * AskAIButton - Reusable "Ask AI" button component
 *
 * Used in:
 * - Chatter
 * - Form header
 * - List view actions
 */
export class AskAIButton extends Component {
    static template = "ipai_ask_ai_chatter.AskAIButton";
    static props = {
        // Context to pass to AI
        model: { type: String, optional: true },
        resId: { type: Number, optional: true },
        resIds: { type: Array, optional: true },
        displayName: { type: String, optional: true },
        viewType: { type: String, optional: true },
        // UI options
        size: { type: String, optional: true }, // sm, md, lg
        variant: { type: String, optional: true }, // filled, tonal, outlined, text, icon
        label: { type: String, optional: true },
        showLabel: { type: Boolean, optional: true },
        title: { type: String, optional: true },
        // Callbacks
        onClick: { type: Function, optional: true },
    };
    static defaultProps = {
        size: "md",
        variant: "tonal",
        label: "Ask AI",
        showLabel: true,
        title: "Ask AI about this",
    };

    setup() {
        this.askAi = useService("ask_ai");
        this.context = useService("ask_ai_context");
    }

    get buttonClass() {
        const classes = ["ipai-ask-ai-btn"];
        classes.push(`ipai-ask-ai-btn--${this.props.size || "md"}`);
        classes.push(`ipai-ask-ai-btn--${this.props.variant || "tonal"}`);
        return classes.join(" ");
    }

    /**
     * Handle button click
     */
    onClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        // Build context from props
        const context = {
            model: this.props.model,
            res_id: this.props.resId,
            res_ids: this.props.resIds || [],
            display_name: this.props.displayName,
            view_type: this.props.viewType,
        };

        // Update context service
        this.context.setContext({
            model: context.model,
            resId: context.res_id,
            resIds: context.res_ids,
            displayName: context.display_name,
            viewType: context.view_type,
        });

        // Open AI panel with context
        this.askAi.open(context);

        // Call custom onClick if provided
        if (this.props.onClick) {
            this.props.onClick(context);
        }
    }
}
