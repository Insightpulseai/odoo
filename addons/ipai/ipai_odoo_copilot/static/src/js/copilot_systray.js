/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

/**
 * CopilotSystrayButton — systray icon that opens the copilot chat panel.
 * Self-contained in ipai_odoo_copilot. No dependency on deprecated modules.
 */
export class CopilotSystrayButton extends Component {
    static template = "ipai_odoo_copilot.SystrayButton";

    setup() {
        this.state = useState({
            isOpen: false,
            messages: [],
            isLoading: false,
            error: null,
            isDisabled: false,
        });
        this.inputRef = useRef("promptInput");
        this.messagesRef = useRef("messageList");
        this.action = useService("action");

        // Check if copilot is enabled
        onMounted(async () => {
            try {
                const result = await rpc("/web/dataset/call_kw", {
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["ipai.copilot.foundry_enabled", "False"],
                    kwargs: {},
                });
                this.state.isDisabled = result !== "True";
            } catch {
                this.state.isDisabled = true;
            }
        });
    }

    togglePanel() {
        this.state.isOpen = !this.state.isOpen;
        this.state.error = null;
        if (this.state.isOpen && this.inputRef.el) {
            setTimeout(() => this.inputRef.el?.focus(), 100);
        }
    }

    closePanel() {
        this.state.isOpen = false;
    }

    /**
     * Get current page context (model, record ID, action) when available.
     */
    _getPageContext() {
        const context = {};
        try {
            const controller = this.action.currentController;
            if (controller) {
                const action = controller.action;
                if (action) {
                    context.record_model = action.res_model || null;
                    context.record_id = action.res_id || null;
                    context.surface = "erp";
                }
            }
        } catch {
            // Context capture is best-effort
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
        const prompt = input?.value?.trim();
        if (!prompt || this.state.isLoading) return;

        // Add user message
        this.state.messages.push({
            role: "user",
            content: prompt,
            timestamp: new Date().toLocaleTimeString(),
        });
        input.value = "";
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        try {
            const context = this._getPageContext();
            const result = await rpc("/ipai/copilot/chat", {
                prompt,
                record_model: context.record_model,
                record_id: context.record_id,
                surface: context.surface || "erp",
            });

            if (result.blocked) {
                this.state.messages.push({
                    role: "assistant",
                    content: result.reason || "Response was blocked by safety filters.",
                    blocked: true,
                    timestamp: new Date().toLocaleTimeString(),
                });
            } else {
                this.state.messages.push({
                    role: "assistant",
                    content: result.content || "No response received.",
                    citations: result.citations || [],
                    timestamp: new Date().toLocaleTimeString(),
                });
            }
        } catch (err) {
            const msg = err.message || "Failed to reach copilot. Check Settings → Pulser.";
            this.state.error = msg;
            this.state.messages.push({
                role: "error",
                content: msg,
                timestamp: new Date().toLocaleTimeString(),
            });
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    clearMessages() {
        this.state.messages = [];
        this.state.error = null;
    }

    _scrollToBottom() {
        setTimeout(() => {
            const el = this.messagesRef.el;
            if (el) el.scrollTop = el.scrollHeight;
        }, 50);
    }
}

// Register in systray (rightmost position)
registry.category("systray").add("ipai_odoo_copilot.SystrayButton", {
    Component: CopilotSystrayButton,
    isDisplayed: () => true,
}, { sequence: 1 });
