/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PulserChatPanel extends Component {
    static template = "ipai_pulser_chat.ChatPanel";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.inputRef = useRef("chatInput");
        this.messagesRef = useRef("messageList");

        this.state = useState({
            // Lifecycle: false until bootstrap completes (or fails).
            ready: false,
            enabled: false,
            backendConfigured: false,
            // Indicates a message RPC is in-flight.
            isLoading: false,
            // Bootstrap-specific loading indicator.
            isBootstrapping: true,
            // User-facing error string; null when no error.
            error: null,
            inputValue: "",
            conversationId: null,
            messages: [],
            companyName: "",
        });

        // Guard against calling bootstrap multiple times if the panel is
        // toggled rapidly. Only the first mount within a lifecycle triggers it.
        this._bootstrapDone = false;
        this._destroyed = false;

        onMounted(() => {
            if (!this._bootstrapDone) {
                this._bootstrapDone = true;
                this._bootstrap();
            }
        });

        onWillUnmount(() => {
            // Signal to in-flight async handlers that the component is gone.
            this._destroyed = true;
        });
    }

    async _bootstrap() {
        try {
            const result = await this.rpc("/ipai/pulser_chat/bootstrap", {});
            if (this._destroyed) return;
            this.state.enabled = !!result.enabled;
            this.state.backendConfigured = !!result.backend_configured;
            this.state.companyName = result.company_name || "";
        } catch (err) {
            if (this._destroyed) return;
            // Non-fatal: show a soft error but leave the panel usable.
            this.state.error = "Failed to load Pulser chat settings.";
        } finally {
            if (!this._destroyed) {
                this.state.ready = true;
                this.state.isBootstrapping = false;
            }
        }
    }

    _buildContext() {
        const context = { surface: "erp" };
        try {
            const controller = this.action.currentController;
            const action = controller?.action;
            if (action?.res_model) {
                context.context_model = action.res_model;
            }
            if (action?.res_id) {
                context.context_res_id = action.res_id;
            }
        } catch (_) {
            // action service may not expose a currentController in all surfaces;
            // fall back to surface-only context.
        }
        return context;
    }

    async sendMessage() {
        const text = this.state.inputValue.trim();
        if (!text || this.state.isLoading || !this.state.enabled || !this.state.backendConfigured) {
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

            if (this._destroyed) return;

            if (!result || !result.ok) {
                this.state.error = (result && result.error) || "Pulser chat failed.";
            } else {
                this.state.messages.push({
                    id: Date.now() + 1,
                    role: "assistant",
                    content: result.content || "(No response received.)",
                });
                // Persist conversation ID for multi-turn context.
                if (result.conversation_id) {
                    this.state.conversationId = result.conversation_id;
                }
            }
        } catch (_err) {
            if (this._destroyed) return;
            this.state.error = "Pulser backend request failed. Check your connection.";
        } finally {
            if (!this._destroyed) {
                this.state.isLoading = false;
                this._scrollToBottom();
            }
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    clearConversation() {
        this.state.messages = [];
        this.state.conversationId = null;
        this.state.error = null;
    }

    _scrollToBottom() {
        // Defer one tick so Owl has finished patching the DOM.
        setTimeout(() => {
            const el = this.messagesRef.el;
            if (el) {
                el.scrollTop = el.scrollHeight;
            }
        }, 50);
    }
}
