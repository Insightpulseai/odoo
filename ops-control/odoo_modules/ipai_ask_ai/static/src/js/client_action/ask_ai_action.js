/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { AskAIPanel } from "../components/ask_ai_panel/ask_ai_panel";

/**
 * AskAIAction - Client action that renders the AI Copilot
 *
 * Can be used:
 * - As a full-page action
 * - Embedded in a side panel
 */
export class AskAIAction extends Component {
    static template = "ipai_ask_ai.AskAIAction";
    static components = { AskAIPanel };
    static props = ["*"];

    setup() {
        this.askAi = useService("ask_ai");
        this.context = useService("ask_ai_context");
        this.action = useService("action");

        this.state = useState({
            layout: this.props.action?.context?.layout || "fullpage", // fullpage | sidebar | floating
        });

        onMounted(() => {
            // Initialize with current context
            this.askAi.open(this.context.getContext());
        });
    }

    get layoutClass() {
        return `ipai-action-layout ipai-action-layout--${this.state.layout}`;
    }

    /**
     * Close the panel/action
     */
    onClose() {
        this.askAi.close();
        // Navigate back if full page
        if (this.state.layout === "fullpage") {
            this.action.doAction({ type: "ir.actions.act_window_close" });
        }
    }
}

// Register as client action
registry.category("actions").add("ask_ai_panel", AskAIAction);
