/** @odoo-module */

import { Component, useState, useRef, onMounted, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { renderMarkdown } from "./copilot_markdown";

/**
 * CopilotSystrayButton — systray icon that opens the copilot chat panel.
 *
 * Uses the copilot service for gateway communication and conversation state.
 * Renders a slide-out panel on the right side with message history.
 */
export class CopilotSystrayButton extends Component {
    static template = "ipai_odoo_copilot.SystrayButton";

    setup() {
        this.state = useState({
            isOpen: false,
            messages: [],
            isLoading: false,
            error: null,
        });
        this.inputRef = useRef("promptInput");
        this.messagesRef = useRef("messageList");
        this.copilot = useService("copilot");
        this.action = useService("action");
    }

    togglePanel() {
        this.state.isOpen = !this.state.isOpen;
        this.state.error = null;
        if (this.state.isOpen) {
            setTimeout(() => {
                const el = this.inputRef.el;
                if (el) {
                    el.focus();
                }
            }, 150);
        }
    }

    closePanel() {
        this.state.isOpen = false;
    }

    /**
     * Capture current page context (model, record ID) from the action service.
     */
    _getPageContext() {
        const context = {};
        try {
            const controller = this.action.currentController;
            if (controller && controller.action) {
                const act = controller.action;
                context.context_model = act.res_model || "";
                context.context_res_id = act.res_id || 0;
                context.surface = "erp";
            }
        } catch {
            // Context capture is best-effort — do not break on failure
        }
        return context;
    }

    async onKeyDown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            await this.sendMessage();
        }
    }

    async sendMessage() {
        const input = this.inputRef.el;
        const text = (input && input.value || "").trim();
        if (!text || this.state.isLoading) {
            return;
        }

        // Show user message immediately
        this.state.messages.push({
            role: "user",
            content: text,
            timestamp: new Date().toLocaleTimeString(),
        });
        input.value = "";
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        const context = this._getPageContext();

        // Add empty assistant bubble for streaming content
        const assistantMsg = {
            role: "assistant",
            content: "",
            latency_ms: 0,
            timestamp: new Date().toLocaleTimeString(),
            streaming: true,
        };
        this.state.messages.push(assistantMsg);
        const msgIndex = this.state.messages.length - 1;

        try {
            const result = await this.copilot.sendMessageStreaming(
                text,
                context,
                (fullText) => {
                    // Update the assistant message reactively as chunks arrive
                    this.state.messages[msgIndex] = {
                        ...this.state.messages[msgIndex],
                        content: fullText,
                    };
                    this._scrollToBottom();
                },
            );

            // Finalize the message
            this.state.messages[msgIndex] = {
                ...this.state.messages[msgIndex],
                content: result.content || assistantMsg.content || "No response received.",
                latency_ms: result.latency_ms || 0,
                streaming: false,
            };
        } catch (streamErr) {
            // Remove the empty streaming bubble on failure
            if (!assistantMsg.content) {
                this.state.messages.splice(msgIndex, 1);
            }

            // Fallback to non-streaming RPC
            try {
                const result = await this.copilot.sendMessage(text, context);
                if (result.error) {
                    this.state.error = result.message || "Unknown error";
                    this.state.messages.push({
                        role: "error",
                        content: result.message || "An error occurred.",
                        timestamp: new Date().toLocaleTimeString(),
                    });
                } else {
                    this.state.messages.push({
                        role: "assistant",
                        content: result.content || "No response received.",
                        latency_ms: result.latency_ms || 0,
                        timestamp: new Date().toLocaleTimeString(),
                    });
                }
            } catch (rpcErr) {
                const msg = rpcErr.message
                    || "Failed to reach copilot gateway. Check connection settings.";
                this.state.error = msg;
                this.state.messages.push({
                    role: "error",
                    content: msg,
                    timestamp: new Date().toLocaleTimeString(),
                });
            }
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    /**
     * Render markdown content as safe HTML for use with t-out.
     * @param {string} content
     * @returns {Markup}
     */
    renderContent(content) {
        return markup(renderMarkdown(content || ""));
    }

    clearMessages() {
        this.state.messages = [];
        this.state.error = null;
        this.copilot.resetConversation();
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

// Register in systray — sequence 1 puts it on the right side
registry.category("systray").add("ipai_odoo_copilot.SystrayButton", {
    Component: CopilotSystrayButton,
    isDisplayed: () => true,
}, { sequence: 1 });
