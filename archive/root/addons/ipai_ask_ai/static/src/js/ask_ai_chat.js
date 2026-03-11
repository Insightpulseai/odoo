/** @odoo-module **/
/**
 * Ask AI Chat Panel Component
 *
 * The main chat window component for AI conversations.
 * Implements the full chat UI with message display, input, and actions.
 */

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * AskAIChat - Main chat panel component
 */
export class AskAIChat extends Component {
    static template = "ipai_ask_ai.ChatPanel";
    static props = {
        onClose: { type: Function, optional: true },
        onMinimize: { type: Function, optional: true },
    };

    setup() {
        // Services
        this.askAI = useService("askAI");
        this.notification = useService("notification");

        // Refs
        this.inputRef = useRef("messageInput");
        this.messagesRef = useRef("messagesContainer");

        // State
        this.state = useState({
            isOpen: true,
            isMinimized: false,
            isLoading: false,
            isTyping: false,
            messages: [],
            inputValue: "",
            hasUnread: false,
            suggestions: [],
            showSuggestions: true,
            error: null,
        });

        // Default suggestions
        this.defaultSuggestions = [
            { text: "Do I have any customers in Japan?", icon: "fa-users" },
            { text: "Sales this month", icon: "fa-chart-line" },
            { text: "Show unpaid invoices", icon: "fa-file-invoice" },
            { text: "My assigned tasks", icon: "fa-tasks" },
            { text: "Help", icon: "fa-question-circle" },
        ];

        onWillStart(async () => {
            await this.initialize();
        });

        onMounted(() => {
            this.setupKeyboardShortcuts();
            this.focusInput();
        });
    }

    /**
     * Initialize the chat
     */
    async initialize() {
        try {
            await this.askAI.initialize();
            this.state.suggestions = this.defaultSuggestions;

            // Add welcome message
            this.addMessage({
                type: "ai",
                content: _t("Hello! I'm your AI assistant. Ask me anything about your business data."),
                timestamp: new Date(),
            });
        } catch (error) {
            console.error("[AskAI] Initialization error:", error);
            this.state.error = _t("Failed to initialize AI chat. Please refresh the page.");
        }
    }

    /**
     * Add a message to the chat
     */
    addMessage(message) {
        this.state.messages.push({
            id: Date.now(),
            ...message,
        });
        this.scrollToBottom();
    }

    /**
     * Send a message
     */
    async sendMessage() {
        const content = this.state.inputValue.trim();
        if (!content || this.state.isTyping) return;

        // Add user message
        this.addMessage({
            type: "user",
            content: content,
            timestamp: new Date(),
        });

        // Clear input
        this.state.inputValue = "";
        this.state.showSuggestions = false;
        this.state.isTyping = true;

        try {
            // Get AI response
            const result = await this.askAI.sendMessage(content);

            // Add AI response
            this.addMessage({
                type: "ai",
                content: result.ai_response || result.response || _t("I couldn't process that request."),
                timestamp: new Date(),
                data: result.data,
                action: result.action,
            });

            this.state.hasUnread = true;
        } catch (error) {
            console.error("[AskAI] Send error:", error);
            this.addMessage({
                type: "error",
                content: _t("Failed to get a response. Please try again."),
                timestamp: new Date(),
            });
        } finally {
            this.state.isTyping = false;
            this.focusInput();
        }
    }

    /**
     * Handle input keydown
     */
    onKeydown(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        } else if (event.key === "Escape") {
            this.close();
        }
    }

    /**
     * Handle input change
     */
    onInput(event) {
        this.state.inputValue = event.target.value;
        this.updateSuggestions();
    }

    /**
     * Update suggestions based on input
     */
    updateSuggestions() {
        const query = this.state.inputValue.toLowerCase();
        if (!query) {
            this.state.suggestions = this.defaultSuggestions;
            this.state.showSuggestions = true;
        } else {
            this.state.suggestions = this.defaultSuggestions.filter(s =>
                s.text.toLowerCase().includes(query)
            );
            this.state.showSuggestions = this.state.suggestions.length > 0;
        }
    }

    /**
     * Select a suggestion
     */
    selectSuggestion(suggestion) {
        this.state.inputValue = suggestion.text;
        this.state.showSuggestions = false;
        this.sendMessage();
    }

    /**
     * Mark messages as read
     */
    markAsRead() {
        this.state.hasUnread = false;
    }

    /**
     * Minimize the chat window
     */
    minimize() {
        this.state.isMinimized = !this.state.isMinimized;
        if (this.props.onMinimize) {
            this.props.onMinimize(this.state.isMinimized);
        }
    }

    /**
     * Close the chat window
     */
    close() {
        this.state.isOpen = false;
        if (this.props.onClose) {
            this.props.onClose();
        }
    }

    /**
     * Clear chat history
     */
    clearHistory() {
        this.state.messages = [];
        this.addMessage({
            type: "ai",
            content: _t("Chat cleared. How can I help you?"),
            timestamp: new Date(),
        });
    }

    /**
     * Execute an action from AI response
     */
    async executeAction(action) {
        if (!action) return;

        try {
            const actionService = this.env.services.action;
            await actionService.doAction(action);
        } catch (error) {
            console.error("[AskAI] Action error:", error);
            this.notification.add(_t("Failed to execute action"), { type: "danger" });
        }
    }

    /**
     * Scroll messages to bottom
     */
    scrollToBottom() {
        requestAnimationFrame(() => {
            const container = this.messagesRef.el;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        });
    }

    /**
     * Focus the input field
     */
    focusInput() {
        requestAnimationFrame(() => {
            const input = this.inputRef.el;
            if (input) {
                input.focus();
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener("keydown", (e) => {
            // Ctrl/Cmd + Shift + A to toggle Ask AI
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "a") {
                e.preventDefault();
                if (!this.state.isOpen) {
                    this.state.isOpen = true;
                    this.focusInput();
                }
            }
        });
    }

    /**
     * Format timestamp for display
     */
    formatTime(date) {
        if (!date) return "";
        const d = new Date(date);
        return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    /**
     * Get message class based on type
     */
    getMessageClass(message) {
        const classes = ["o_ask_ai_message"];
        classes.push(`o_ask_ai_message_${message.type}`);
        return classes.join(" ");
    }
}
