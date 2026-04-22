/** @odoo-module **/

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PulserChatPanel extends Component {
    static template = "ipai_pulser_chat.ChatPanel";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.inputRef = useRef("chatInput");
        this.messagesRef = useRef("messageList");
        this.state = useState({
            ready: false,
            enabled: false,
            backendConfigured: false,
            isLoading: false,
            error: null,
            inputValue: "",
            conversationId: null,
            messages: [],
            companyName: "",
        });

        onMounted(async () => {
            await this._bootstrap();
        });
    }

    async _bootstrap() {
        try {
            const result = await this.rpc("/ipai/pulser_chat/bootstrap", {});
            this.state.enabled = !!result.enabled;
            this.state.backendConfigured = !!result.backend_configured;
            this.state.companyName = result.company_name || "";
        } catch {
            this.state.error = "Failed to load Pulser chat settings.";
        } finally {
            this.state.ready = true;
        }
    }

    _buildContext() {
        const context = { surface: "erp" };
        const controller = this.action.currentController;
        const action = controller?.action;
        if (action?.res_model) {
            context.context_model = action.res_model;
        }
        if (action?.res_id) {
            context.context_res_id = action.res_id;
        }
        return context;
    }

    async sendMessage() {
        const text = this.state.inputValue.trim();
        if (!text || this.state.isLoading || !this.state.enabled) {
            return;
        }

        this.state.messages.push({
            id: Date.now(),
            role: "user",
            content: text,
        });
        this.state.inputValue = "";
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        try {
            const result = await this.rpc("/ipai/pulser_chat/message", {
                message: text,
                context: this._buildContext(),
                conversation_id: this.state.conversationId,
            });
            if (!result.ok) {
                this.state.error = result.error || "Pulser chat failed.";
            } else {
                this.state.messages.push({
                    id: Date.now() + 1,
                    role: "assistant",
                    content: result.content || "No response received.",
                });
                this.state.conversationId = result.conversation_id || this.state.conversationId;
            }
        } catch {
            this.state.error = "Pulser backend request failed.";
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    _scrollToBottom() {
        setTimeout(() => {
            const el = this.messagesRef.el;
            if (el) {
                el.scrollTop = el.scrollHeight;
            }
        }, 50);
    }
}
