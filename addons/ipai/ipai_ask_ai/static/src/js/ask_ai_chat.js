/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AskAIChat extends Component {
    static template = "ipai_ask_ai.AskAIChat";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            messages: [],
            currentInput: "",
            loading: false,
            conversationId: null,
        });

        this.inputRef = useRef("input");
        this.messagesRef = useRef("messages");

        onMounted(() => {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
        });
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

        // Add user message to display
        this.state.messages.push({
            role: "user",
            content: input,
            timestamp: new Date().toISOString(),
        });
        this.state.currentInput = "";
        this.state.loading = true;

        // Scroll to bottom
        this._scrollToBottom();

        try {
            // Call the API
            const result = await this.rpc("/ipai/ask_ai/query", {
                prompt: input,
                res_model: this.props.resModel || null,
                res_id: this.props.resId || null,
            });

            if (result.success) {
                this.state.messages.push({
                    role: "assistant",
                    content: result.response,
                    timestamp: new Date().toISOString(),
                });
                this.state.conversationId = result.conversation_id;
            } else {
                this.notification.add(result.error || "Failed to get response", {
                    type: "danger",
                });
            }
        } catch (error) {
            console.error("Ask AI error:", error);
            this.notification.add("An error occurred while processing your request", {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
            this._scrollToBottom();
        }
    }

    _scrollToBottom() {
        setTimeout(() => {
            if (this.messagesRef.el) {
                this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
            }
        }, 100);
    }

    onClear() {
        this.state.messages = [];
        this.state.conversationId = null;
    }

    formatContent(content) {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/## (.*?)$/gm, "<h4>$1</h4>")
            .replace(/- (.*?)$/gm, "<li>$1</li>")
            .replace(/\n/g, "<br>");
    }
}

// Register as a client action
registry.category("actions").add("ipai_ask_ai.chat", AskAIChat);
