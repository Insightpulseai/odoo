/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";

/**
 * Composer - Chat input component with multiline support
 *
 * Features:
 * - Auto-expanding textarea
 * - Submit on Enter (Shift+Enter for newline)
 * - Attachment support (future)
 * - Loading state
 */
export class Composer extends Component {
    static template = "ipai_ask_ai.Composer";
    static props = {
        onSend: Function,
        isLoading: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            value: "",
            isFocused: false,
        });
        this.textareaRef = useRef("textarea");

        onMounted(() => {
            this.adjustHeight();
        });
    }

    get canSend() {
        return this.state.value.trim().length > 0 && !this.props.isLoading;
    }

    get composerClass() {
        const classes = ["ipai-composer"];
        if (this.state.isFocused) classes.push("ipai-composer--focused");
        if (this.props.isLoading) classes.push("ipai-composer--loading");
        return classes.join(" ");
    }

    /**
     * Handle input change
     */
    onInput(ev) {
        this.state.value = ev.target.value;
        this.adjustHeight();
    }

    /**
     * Handle key down
     */
    onKeyDown(ev) {
        // Submit on Enter (without Shift)
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.send();
        }
    }

    /**
     * Handle focus
     */
    onFocus() {
        this.state.isFocused = true;
    }

    /**
     * Handle blur
     */
    onBlur() {
        this.state.isFocused = false;
    }

    /**
     * Adjust textarea height to content
     */
    adjustHeight() {
        const textarea = this.textareaRef.el;
        if (textarea) {
            textarea.style.height = "auto";
            const newHeight = Math.min(textarea.scrollHeight, 200);
            textarea.style.height = `${newHeight}px`;
        }
    }

    /**
     * Send the message
     */
    send() {
        if (!this.canSend) return;

        const value = this.state.value.trim();
        this.props.onSend(value);
        this.state.value = "";

        // Reset height
        const textarea = this.textareaRef.el;
        if (textarea) {
            textarea.style.height = "auto";
        }
    }

    /**
     * Focus the textarea
     */
    focus() {
        this.textareaRef.el?.focus();
    }
}
