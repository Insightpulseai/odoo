/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";

/**
 * Ask AI Chatter Widget Component
 *
 * Provides a popup chat interface within the Chatter for contextual AI assistance.
 */
export class AskAIChatterWidget extends Component {
    static template = "ipai_ask_ai_chatter.AskAIWidget";
    static props = {
        resModel: String,
        resId: Number,
        onClose: Function,
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            messages: [],
            currentInput: "",
            loading: false,
        });

        this.inputRef = useRef("input");
    }

    get hasMessages() {
        return this.state.messages.length > 0;
    }

    async onInputKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            await this.onSend();
        }
    }

    async onSend() {
        const input = this.state.currentInput.trim();
        if (!input || this.state.loading) {
            return;
        }

        this.state.messages.push({
            role: "user",
            content: input,
        });
        this.state.currentInput = "";
        this.state.loading = true;

        try {
            const result = await this.rpc("/ipai/ask_ai/query", {
                prompt: input,
                res_model: this.props.resModel,
                res_id: this.props.resId,
            });

            if (result.success) {
                this.state.messages.push({
                    role: "assistant",
                    content: result.response,
                });
            } else {
                this.notification.add(result.error || "Failed to get response", {
                    type: "danger",
                });
            }
        } catch (error) {
            console.error("Ask AI Chatter error:", error);
            this.notification.add("An error occurred", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    formatContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/## (.*?)$/gm, "<h5>$1</h5>")
            .replace(/- (.*?)$/gm, "<li>$1</li>")
            .replace(/\n/g, "<br>");
    }
}

/**
 * Patch Chatter to add Ask AI button
 */
patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.askAiState = useState({
            showWidget: false,
        });
    },

    toggleAskAI() {
        this.askAiState.showWidget = !this.askAiState.showWidget;
    },

    closeAskAI() {
        this.askAiState.showWidget = false;
    },
});

// Register the widget component
registry.category("components").add("AskAIChatterWidget", AskAIChatterWidget);
