/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { ActionChip } from "../action_chip/action_chip";
import { Citation } from "../citation/citation";
import { DiffPreview } from "../diff_preview/diff_preview";

/**
 * Message - Individual chat message component
 *
 * Supports:
 * - User and assistant messages
 * - Markdown rendering
 * - Citations list
 * - Action chips
 * - Diff preview
 * - Loading state
 */
export class Message extends Component {
    static template = "ipai_ask_ai.Message";
    static components = { ActionChip, Citation, DiffPreview };
    static props = {
        message: Object,
        onExecuteAction: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({
            expandedAction: null,
            showAllCitations: false,
        });
    }

    get isUser() {
        return this.props.message.role === "user";
    }

    get isAssistant() {
        return this.props.message.role === "assistant";
    }

    get isSystem() {
        return this.props.message.role === "system";
    }

    get isLoading() {
        return this.props.message.isLoading;
    }

    get content() {
        return this.props.message.content || "";
    }

    get citations() {
        return this.props.message.citations || [];
    }

    get actions() {
        return this.props.message.actions || [];
    }

    get displayedCitations() {
        if (this.state.showAllCitations) {
            return this.citations;
        }
        return this.citations.slice(0, 3);
    }

    get hasMoreCitations() {
        return this.citations.length > 3;
    }

    get timestamp() {
        const date = this.props.message.create_date;
        if (!date) return "";
        const d = new Date(date);
        return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    get messageClass() {
        const classes = ["ipai-message", "ipai-message-enter"];
        if (this.isUser) classes.push("ipai-message--user");
        if (this.isAssistant) classes.push("ipai-message--assistant");
        if (this.isSystem) classes.push("ipai-message--system");
        if (this.isLoading) classes.push("ipai-message--loading");
        return classes.join(" ");
    }

    /**
     * Render markdown content to HTML
     * Note: In production, use a proper markdown library like marked.js
     */
    renderMarkdown(content) {
        if (!content) return "";

        // Basic markdown rendering (simplified)
        let html = content
            // Escape HTML
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            // Bold
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            // Italic
            .replace(/\*(.+?)\*/g, "<em>$1</em>")
            // Code blocks
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="ipai-code-block"><code>$2</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code class="ipai-code">$1</code>')
            // Headers
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            // Lists
            .replace(/^\* (.+)$/gm, '<li>$1</li>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
            // Blockquotes
            .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
            // Line breaks
            .replace(/\n\n/g, "</p><p>")
            .replace(/\n/g, "<br>");

        // Wrap in paragraph
        html = `<p>${html}</p>`;

        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, "");

        // Wrap consecutive list items
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');

        return html;
    }

    /**
     * Handle action click
     */
    onActionClick(actionIndex) {
        const action = this.actions[actionIndex];
        if (action.preview_diff) {
            // Toggle diff preview
            this.state.expandedAction =
                this.state.expandedAction === actionIndex ? null : actionIndex;
        } else {
            // Execute immediately if no preview needed
            this.executeAction(actionIndex);
        }
    }

    /**
     * Execute an action
     */
    executeAction(actionIndex) {
        if (this.props.onExecuteAction) {
            this.props.onExecuteAction(actionIndex);
        }
    }

    /**
     * Toggle show all citations
     */
    toggleCitations() {
        this.state.showAllCitations = !this.state.showAllCitations;
    }
}
