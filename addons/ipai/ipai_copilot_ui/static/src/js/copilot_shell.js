/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * IPAI Copilot Shell Component
 * Microsoft 365 Copilot-inspired UI for Odoo CE 18
 *
 * Features:
 * - Fluent 2 design language
 * - Chat-based interaction shell
 * - Tool cards for AI capabilities
 * - Sidebar navigation
 */
export class CopilotShell extends Component {
    static template = "ipai_copilot_ui.CopilotShell";
    static props = {};

    setup() {
        // Services
        try {
            this.rpc = useService("rpc");
        } catch (e) {
            console.warn("[CopilotShell] RPC service not available:", e);
            this.rpc = null;
        }

        try {
            this.notification = useService("notification");
        } catch (e) {
            console.warn("[CopilotShell] Notification service not available:", e);
            this.notification = null;
        }

        try {
            this.action = useService("action");
        } catch (e) {
            console.warn("[CopilotShell] Action service not available:", e);
            this.action = null;
        }

        // State
        this.state = useState({
            // Navigation
            activeNav: "chat",

            // Chat state
            messages: [],
            currentInput: "",
            isLoading: false,

            // Conversations
            conversations: [
                { id: 1, title: "Previous conversation", date: "Today" },
            ],

            // Tools configuration
            tools: [
                {
                    id: "analyze",
                    title: "Analyze Data",
                    subtitle: "Get insights from your business data",
                    icon: "fa-chart-line",
                    iconClass: "analyze",
                },
                {
                    id: "create",
                    title: "Create Content",
                    subtitle: "Draft emails, reports, and documents",
                    icon: "fa-pen-fancy",
                    iconClass: "create",
                },
                {
                    id: "search",
                    title: "Search Records",
                    subtitle: "Find customers, orders, and more",
                    icon: "fa-search",
                    iconClass: "search",
                },
                {
                    id: "assistant",
                    title: "AI Assistant",
                    subtitle: "Get help with any task",
                    icon: "fa-robot",
                    iconClass: "assistant",
                },
            ],

            // Quick actions / suggestions
            quickActions: [
                "What are my pending tasks?",
                "Summarize recent sales",
                "Draft a follow-up email",
                "Show overdue invoices",
            ],

            // Placeholder text
            promptPlaceholder:
                "Ask me anything about your business data, draft content, or get help with tasks...",
        });

        // Refs
        this.inputRef = useRef("promptInput");
        this.messagesRef = useRef("messagesContainer");

        // Lifecycle
        onMounted(() => {
            this._focusInput();
        });
    }

    // =========================================
    // Navigation
    // =========================================

    onNavClick(navId) {
        this.state.activeNav = navId;
    }

    isNavActive(navId) {
        return this.state.activeNav === navId;
    }

    // =========================================
    // Chat Interaction
    // =========================================

    get hasMessages() {
        return this.state.messages.length > 0;
    }

    onInputChange(ev) {
        this.state.currentInput = ev.target.value;
    }

    onInputKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.onSend();
        }
    }

    async onSend() {
        const input = this.state.currentInput.trim();
        if (!input || this.state.isLoading) {
            return;
        }

        // Add user message
        this.state.messages.push({
            id: Date.now(),
            role: "user",
            content: input,
            timestamp: new Date().toISOString(),
        });

        this.state.currentInput = "";
        this.state.isLoading = true;
        this._scrollToBottom();

        try {
            // Simulate AI response (replace with actual API call)
            await this._simulateResponse(input);
        } catch (error) {
            console.error("[CopilotShell] Error sending message:", error);
            if (this.notification) {
                this.notification.add("Failed to get response", { type: "danger" });
            }
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    async _simulateResponse(userInput) {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Generate a contextual response
        let response = "";
        const lowerInput = userInput.toLowerCase();

        if (lowerInput.includes("task") || lowerInput.includes("pending")) {
            response = `Here are your pending tasks:\n\n1. **Review Q4 budget proposal** - Due tomorrow\n2. **Approve vendor invoices** - 3 items pending\n3. **Complete month-end reconciliation** - Due in 2 days\n\nWould you like me to help with any of these?`;
        } else if (lowerInput.includes("sales") || lowerInput.includes("revenue")) {
            response = `**Sales Summary (Last 30 Days)**\n\n- Total Revenue: $124,500\n- Orders: 47\n- Average Order Value: $2,649\n- Top Product: Enterprise License (+23%)\n\nWould you like a detailed breakdown by region or product?`;
        } else if (lowerInput.includes("email") || lowerInput.includes("draft")) {
            response = `I can help you draft an email. Here's a template:\n\n---\n\n**Subject:** Follow-up on Our Recent Discussion\n\nDear [Name],\n\nThank you for taking the time to meet with us. I wanted to follow up on the key points we discussed...\n\n---\n\nWould you like me to customize this further?`;
        } else if (lowerInput.includes("invoice") || lowerInput.includes("overdue")) {
            response = `**Overdue Invoices**\n\n| Customer | Amount | Days Overdue |\n|----------|--------|-------------|\n| Acme Corp | $5,200 | 15 days |\n| Tech Inc | $3,800 | 8 days |\n| Global Ltd | $2,100 | 3 days |\n\n**Total Overdue:** $11,100\n\nWould you like me to draft reminder emails for these customers?`;
        } else {
            response = `I understand you're asking about "${userInput}". As your AI assistant, I can help you:\n\n- **Analyze** business data and generate reports\n- **Search** for records, customers, or transactions\n- **Draft** emails, documents, and content\n- **Automate** routine tasks and workflows\n\nCould you provide more details about what you need?`;
        }

        // Add assistant response
        this.state.messages.push({
            id: Date.now(),
            role: "assistant",
            content: response,
            timestamp: new Date().toISOString(),
        });
    }

    onQuickActionClick(action) {
        this.state.currentInput = action;
        this._focusInput();
    }

    onClearChat() {
        this.state.messages = [];
    }

    // =========================================
    // Tool Cards
    // =========================================

    onToolCardClick(tool) {
        // Set a contextual prompt based on the tool
        const prompts = {
            analyze: "Help me analyze my recent business performance",
            create: "Help me draft a professional email",
            search: "Find all customers from last month",
            assistant: "What can you help me with today?",
        };

        this.state.currentInput = prompts[tool.id] || "";
        this._focusInput();
    }

    // =========================================
    // Conversation History
    // =========================================

    onConversationClick(conversation) {
        // In a real implementation, this would load the conversation
        console.log("[CopilotShell] Load conversation:", conversation.id);
    }

    onNewConversation() {
        this.state.messages = [];
        this.state.currentInput = "";
        this._focusInput();
    }

    // =========================================
    // Utilities
    // =========================================

    _focusInput() {
        setTimeout(() => {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
        }, 100);
    }

    _scrollToBottom() {
        setTimeout(() => {
            if (this.messagesRef.el) {
                this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
            }
        }, 100);
    }

    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n\n/g, "</p><p>")
            .replace(/\n/g, "<br>")
            .replace(/^/, "<p>")
            .replace(/$/, "</p>");
    }

    getAvatarInitial(role) {
        return role === "user" ? "U" : "AI";
    }
}

// Register as a client action
registry.category("actions").add("ipai_copilot_shell", CopilotShell);
