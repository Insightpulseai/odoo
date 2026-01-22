/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Message } from "../message/message";
import { Composer } from "../composer/composer";

/**
 * AskAIPanel - Main Copilot side panel component
 *
 * Layout:
 * - Header with context breadcrumb + mode selector + close button
 * - Message list (scrollable)
 * - Composer input at bottom
 */
export class AskAIPanel extends Component {
    static template = "ipai_ask_ai.AskAIPanel";
    static components = { Message, Composer };
    static props = {
        onClose: { type: Function, optional: true },
    };

    setup() {
        this.askAi = useService("ask_ai");
        this.context = useService("ask_ai_context");
        this.messageListRef = useRef("messageList");

        this.state = useState({
            showModeSelector: false,
        });

        // Keyboard shortcut handler
        this.handleKeyDown = this.handleKeyDown.bind(this);
        onMounted(() => {
            document.addEventListener("keydown", this.handleKeyDown);
            this.scrollToBottom();
        });
        onWillUnmount(() => {
            document.removeEventListener("keydown", this.handleKeyDown);
        });
    }

    get messages() {
        return this.askAi.state.messages || [];
    }

    get isLoading() {
        return this.askAi.state.isLoading;
    }

    get currentMode() {
        return this.askAi.state.mode;
    }

    get contextInfo() {
        return this.context.getContext();
    }

    get hasContext() {
        return this.context.hasRecordContext();
    }

    /**
     * Handle sending a message
     */
    async onSendMessage(prompt) {
        if (!prompt.trim()) return;

        try {
            await this.askAi.sendMessage(prompt, this.contextInfo);
            // Scroll to bottom after new message
            this.scrollToBottom();
        } catch (e) {
            console.error("Error sending message:", e);
        }
    }

    /**
     * Handle action execution from a message
     */
    async onExecuteAction(messageId, actionIndex) {
        try {
            await this.askAi.executeAction(messageId, actionIndex);
        } catch (e) {
            console.error("Error executing action:", e);
        }
    }

    /**
     * Change interaction mode
     */
    setMode(mode) {
        this.askAi.setMode(mode);
        this.state.showModeSelector = false;
    }

    /**
     * Toggle mode selector dropdown
     */
    toggleModeSelector() {
        this.state.showModeSelector = !this.state.showModeSelector;
    }

    /**
     * Start a new conversation
     */
    newConversation() {
        this.askAi.clearConversation();
        this.askAi.createConversation(this.contextInfo);
    }

    /**
     * Close the panel
     */
    close() {
        if (this.props.onClose) {
            this.props.onClose();
        } else {
            this.askAi.close();
        }
    }

    /**
     * Scroll message list to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            const el = this.messageListRef.el;
            if (el) {
                el.scrollTop = el.scrollHeight;
            }
        }, 50);
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyDown(ev) {
        // Escape to close
        if (ev.key === "Escape") {
            this.close();
        }
    }

    /**
     * Get mode icon
     */
    getModeIcon(mode) {
        const icons = {
            ask: "fa-question-circle",
            do: "fa-play-circle",
            explain: "fa-info-circle",
        };
        return icons[mode] || "fa-question-circle";
    }

    /**
     * Get mode label
     */
    getModeLabel(mode) {
        const labels = {
            ask: "Ask",
            do: "Do",
            explain: "Explain",
        };
        return labels[mode] || "Ask";
    }
}
