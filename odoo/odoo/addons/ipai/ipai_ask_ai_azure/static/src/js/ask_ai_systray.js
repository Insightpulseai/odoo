/** @odoo-module **/
/**
 * ipai_ask_ai_azure — Owl systray "Ask AI" component for Odoo 19 CE.
 *
 * Registered in registry.category("systray") so it appears in the navbar.
 * Sends prompts to /ipai/ask_ai/chat (Azure OpenAI proxy controller).
 * Azure credentials never reach the browser.
 */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AskAiSystray extends Component {
    static template = "ipai_ask_ai_azure.AskAiSystray";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.state = useState({
            open: false,
            prompt: "",
            loading: false,
            error: "",
            conversationId: null,
            messages: [
                {
                    role: "assistant",
                    text: "Ask anything about your workflow, records, or process context.",
                },
            ],
        });
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    async send() {
        const prompt = this.state.prompt.trim();
        if (!prompt || this.state.loading) {
            return;
        }

        this.state.error = "";
        this.state.loading = true;
        this.state.messages.push({ role: "user", text: prompt });
        this.state.prompt = "";

        try {
            const result = await this.rpc("/ipai/ask_ai/chat", {
                prompt,
                conversation_id: this.state.conversationId,
            });

            if (!result?.ok) {
                throw new Error(result?.error || "Unknown Ask AI error");
            }

            this.state.conversationId = result.conversation_id || this.state.conversationId;
            this.state.messages.push({
                role: "assistant",
                text: result.answer || "No response returned.",
            });
        } catch (err) {
            const message = err?.message || "Failed to contact Ask AI";
            this.state.error = message;
            this.state.messages.push({
                role: "assistant",
                text: `Error: ${message}`,
            });
            this.notification.add(message, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.send();
        }
    }
}

export const systrayItem = {
    Component: AskAiSystray,
};

registry.category("systray").add("ipai_ask_ai_azure.ask_ai_systray", systrayItem, {
    sequence: 10,
});
