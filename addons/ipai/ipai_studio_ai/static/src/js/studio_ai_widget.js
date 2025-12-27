/** @odoo-module **/

/**
 * IPAI Studio AI Widget
 *
 * Floating chat-style panel for natural language Odoo customizations.
 * Uses proper Odoo 18 OWL patterns with service injection.
 */

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Studio AI Chat Panel
 *
 * A floating chat-like panel that processes natural language commands.
 */
export class StudioAIChatPanel extends Component {
    static template = "ipai_studio_ai.ChatPanel";
    static props = {
        onClose: { type: Function, optional: true },
    };

    setup() {
        // Properly inject services using useService hook
        this.rpcService = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.user = useService("user");

        this.inputRef = useRef("commandInput");

        this.state = useState({
            isOpen: true,
            isMinimized: false,
            isProcessing: false,
            command: "",
            messages: [],
            suggestions: [],
            showSuggestions: false,
            currentModel: null,
            currentModelName: null,
        });

        // Context-aware example commands
        this.defaultSuggestions = [
            { text: "Add a phone number field to contacts", icon: "fa-phone" },
            { text: "Create a status dropdown on this model", icon: "fa-list" },
            { text: "When record is created, send notification", icon: "fa-bell" },
            { text: "Add a notes field to this form", icon: "fa-sticky-note" },
            { text: "Show my overdue tasks", icon: "fa-tasks" },
        ];

        // Model-specific suggestions
        this.modelSuggestions = {
            "res.partner": [
                { text: "Add a customer rating field", icon: "fa-star" },
                { text: "Create a VIP checkbox", icon: "fa-crown" },
                { text: "Add industry dropdown", icon: "fa-industry" },
            ],
            "sale.order": [
                { text: "Add a priority field", icon: "fa-flag" },
                { text: "Create approval status dropdown", icon: "fa-check-circle" },
                { text: "When order confirmed, notify sales manager", icon: "fa-bell" },
            ],
            "project.task": [
                { text: "Add effort estimation field", icon: "fa-clock" },
                { text: "Create blocker checkbox", icon: "fa-ban" },
                { text: "Add review status dropdown", icon: "fa-eye" },
            ],
            "account.move": [
                { text: "Add payment reference field", icon: "fa-money" },
                { text: "Create approval workflow trigger", icon: "fa-check" },
                { text: "When invoice posted, send to accounting", icon: "fa-envelope" },
            ],
            "hr.expense": [
                { text: "Add receipt attachment required checkbox", icon: "fa-paperclip" },
                { text: "Create expense category dropdown", icon: "fa-folder" },
            ],
        };

        onWillStart(async () => {
            await this.detectCurrentContext();
        });

        onMounted(() => {
            this.setupKeyboardShortcuts();
            // Focus input after mount
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
            // Initialize suggestions
            this.state.suggestions = this.getSuggestions();
            this.state.showSuggestions = true;
        });
    }

    /**
     * Detect current model context from URL/action
     */
    async detectCurrentContext() {
        try {
            // Get current URL hash
            const hash = window.location.hash;
            const modelMatch = hash.match(/model=([^&]+)/);
            if (modelMatch) {
                this.state.currentModel = modelMatch[1];
                // Get model display name
                const models = await this.orm.searchRead(
                    "ir.model",
                    [["model", "=", this.state.currentModel]],
                    ["name"],
                    { limit: 1 }
                );
                if (models.length) {
                    this.state.currentModelName = models[0].name;
                }
            }
        } catch (e) {
            console.debug("Could not detect current model context:", e);
        }
    }

    /**
     * Get context-aware suggestions
     */
    getSuggestions() {
        if (this.state.currentModel && this.modelSuggestions[this.state.currentModel]) {
            return [
                ...this.modelSuggestions[this.state.currentModel],
                ...this.defaultSuggestions.slice(0, 2),
            ];
        }
        return this.defaultSuggestions;
    }

    /**
     * Minimize panel
     */
    minimizePanel() {
        this.state.isMinimized = true;
    }

    /**
     * Restore from minimized
     */
    restorePanel() {
        this.state.isMinimized = false;
    }

    /**
     * Close panel
     */
    closePanel() {
        this.state.isOpen = false;
        if (this.props.onClose) {
            this.props.onClose();
        }
    }

    /**
     * Handle input changes
     */
    onInput(ev) {
        this.state.command = ev.target.value;
        this.updateSuggestions();
    }

    /**
     * Handle input focus
     */
    onFocus() {
        if (!this.state.command) {
            this.state.suggestions = this.getSuggestions();
            this.state.showSuggestions = true;
        }
    }

    /**
     * Handle input blur
     */
    onBlur() {
        setTimeout(() => {
            this.state.showSuggestions = false;
        }, 200);
    }

    /**
     * Update suggestions based on input
     */
    updateSuggestions() {
        const query = this.state.command.toLowerCase();
        if (!query) {
            this.state.suggestions = this.getSuggestions();
            this.state.showSuggestions = true;
        } else {
            const allSuggestions = [
                ...this.getSuggestions(),
                ...this.defaultSuggestions,
            ];
            // Filter unique suggestions
            const seen = new Set();
            this.state.suggestions = allSuggestions.filter(s => {
                if (seen.has(s.text)) return false;
                seen.add(s.text);
                return s.text.toLowerCase().includes(query);
            });
            this.state.showSuggestions = this.state.suggestions.length > 0;
        }
    }

    /**
     * Select a suggestion
     */
    selectSuggestion(suggestion) {
        this.state.command = suggestion.text;
        this.state.showSuggestions = false;
        if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }

    /**
     * Handle key press in input
     */
    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey && this.state.command.trim()) {
            ev.preventDefault();
            this.sendCommand();
        } else if (ev.key === "Escape") {
            this.closePanel();
        }
    }

    /**
     * Make RPC call to backend
     */
    async callRpc(route, params) {
        try {
            return await this.rpcService(route, params);
        } catch (error) {
            console.error("RPC error:", error);
            throw error;
        }
    }

    /**
     * Send command to backend
     */
    async sendCommand() {
        const command = this.state.command.trim();
        if (!command || this.state.isProcessing) return;

        // Add user message
        this.state.messages.push({
            type: "user",
            content: command,
            timestamp: new Date().toLocaleTimeString(),
        });

        this.state.command = "";
        this.state.isProcessing = true;
        this.state.showSuggestions = false;

        try {
            // Build context
            const context = {};
            if (this.state.currentModel) {
                context.model = this.state.currentModel;
            }

            // Call backend service using properly injected rpc
            const result = await this.callRpc("/web/dataset/call_kw/ipai.studio.ai.service/process_command", {
                model: "ipai.studio.ai.service",
                method: "process_command",
                args: [command, context],
                kwargs: {},
            });

            // Add assistant response
            this.state.messages.push({
                type: "assistant",
                content: result.message || "Command processed.",
                analysis: result.analysis,
                ready: result.ready,
                confidence: result.confidence,
                commandType: result.type,
                timestamp: new Date().toLocaleTimeString(),
            });

            // If ready to execute, offer action
            if (result.ready && result.type === "field") {
                this.state.messages.push({
                    type: "action",
                    content: "Ready to create field. Would you like to proceed?",
                    analysis: result.analysis,
                    timestamp: new Date().toLocaleTimeString(),
                });
            }

            // Handle query results
            if (result.type === "query" && result.records) {
                this.state.messages.push({
                    type: "query_result",
                    content: result.message,
                    records: result.records,
                    action: result.action,
                    timestamp: new Date().toLocaleTimeString(),
                });
            }

        } catch (error) {
            console.error("Studio AI error:", error);
            this.state.messages.push({
                type: "error",
                content: `Error: ${error.message || "Failed to process command"}`,
                timestamp: new Date().toLocaleTimeString(),
            });

            this.notification.add(
                _t("Failed to process command: ") + (error.message || "Unknown error"),
                { type: "danger" }
            );
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Execute a ready command
     */
    async executeCommand(analysis) {
        if (!analysis) return;

        this.state.isProcessing = true;

        try {
            const result = await this.callRpc("/web/dataset/call_kw/ipai.studio.ai.service/execute_field_creation", {
                model: "ipai.studio.ai.service",
                method: "execute_field_creation",
                args: [analysis],
                kwargs: {},
            });

            if (result.success) {
                this.state.messages.push({
                    type: "success",
                    content: result.message || "Field created successfully!",
                    timestamp: new Date().toLocaleTimeString(),
                });

                this.notification.add(
                    _t("Field created successfully!"),
                    { type: "success" }
                );
            } else {
                throw new Error(result.error || "Execution failed");
            }

        } catch (error) {
            console.error("Execution error:", error);
            this.state.messages.push({
                type: "error",
                content: `Execution failed: ${error.message}`,
                timestamp: new Date().toLocaleTimeString(),
            });
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Open query results in a view
     */
    async openQueryResults(actionData) {
        if (actionData) {
            await this.action.doAction(actionData);
        }
    }

    /**
     * Open full wizard
     */
    async openWizard() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Studio AI"),
            res_model: "ipai.studio.ai.wizard",
            view_mode: "form",
            target: "new",
            context: {
                default_command: this.state.command,
            },
        });
    }

    /**
     * Clear chat history
     */
    clearMessages() {
        this.state.messages = [];
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        // Listener is added at document level
    }

    /**
     * Get message CSS class
     */
    getMessageClass(msg) {
        const classes = ["o_studio_ai_message", `o_studio_ai_message-${msg.type}`];
        return classes.join(" ");
    }

    /**
     * Format confidence as percentage
     */
    formatConfidence(confidence) {
        return Math.round((confidence || 0) * 100) + "%";
    }
}

/**
 * Studio AI Systray Item
 *
 * Adds quick access button in the top bar.
 */
export class StudioAISystray extends Component {
    static template = "ipai_studio_ai.Systray";
    static components = { StudioAIChatPanel };
    static props = {};

    setup() {
        this.state = useState({
            showPanel: false,
        });

        // Global keyboard shortcut
        this.boundKeyHandler = this.handleKeydown.bind(this);
        document.addEventListener("keydown", this.boundKeyHandler);
    }

    handleKeydown(e) {
        // Ctrl/Cmd + Shift + A to toggle Studio AI
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "a") {
            e.preventDefault();
            this.togglePanel();
        }
    }

    togglePanel() {
        this.state.showPanel = !this.state.showPanel;
    }

    closePanel() {
        this.state.showPanel = false;
    }
}

// Register systray item
registry.category("systray").add("ipai_studio_ai.Systray", {
    Component: StudioAISystray,
    sequence: 10,
});

/**
 * Utility functions for Studio AI
 */
export const StudioAIUtils = {
    /**
     * Detect field type from natural language
     */
    detectFieldType(text) {
        const patterns = {
            monetary: /\b(price|cost|amount|money|currency|budget)\b/i,
            date: /\b(date|day|when|birthday|deadline)\b/i,
            datetime: /\b(datetime|timestamp)\b/i,
            boolean: /\b(checkbox|yes.?no|flag|toggle)\b/i,
            selection: /\b(dropdown|select|choice|status|type)\b/i,
            text: /\b(notes|comments|description|memo)\b/i,
            integer: /\b(integer|count|quantity|number\s+of)\b/i,
            float: /\b(decimal|rate|percentage)\b/i,
            binary: /\b(file|upload|image|photo|document)\b/i,
        };

        for (const [type, pattern] of Object.entries(patterns)) {
            if (pattern.test(text)) {
                return type;
            }
        }
        return "char";
    },

    /**
     * Detect model from natural language
     */
    detectModel(text) {
        const patterns = {
            "res.partner": /\b(contact|customer|vendor|partner)\b/i,
            "sale.order": /\b(sale|sales?\s*order|quotation)\b/i,
            "purchase.order": /\b(purchase|purchase\s*order)\b/i,
            "account.move": /\b(invoice|bill|journal)\b/i,
            "project.task": /\b(task|todo|ticket)\b/i,
            "project.project": /\b(project)\b/i,
            "hr.employee": /\b(employee|staff)\b/i,
            "product.product": /\b(product|item)\b/i,
        };

        for (const [model, pattern] of Object.entries(patterns)) {
            if (pattern.test(text)) {
                return model;
            }
        }
        return null;
    },

    /**
     * Generate technical name from label
     */
    toTechnicalName(label) {
        return "x_" + label
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "_")
            .replace(/^_+|_+$/g, "");
    },
};
