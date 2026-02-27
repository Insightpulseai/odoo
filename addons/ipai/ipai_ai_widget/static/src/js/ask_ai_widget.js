/** @odoo-module **/
/**
 * IPAI Ask AI Widget — OWL 2 component for Odoo 19 CE
 *
 * Architecture:
 *   OWL button (chatter toolbar)
 *     → AskAiDialog
 *       → JSON-RPC POST /ipai/ai/ask
 *         → Odoo controller (ai_proxy.py)
 *           → IPAI provider bridge (configured via ir.config_parameter)
 *             → LLM (Gemini, etc.)
 *
 * Error codes (from controller):
 *   BRIDGE_URL_NOT_CONFIGURED | AI_KEY_NOT_CONFIGURED | BRIDGE_TIMEOUT | BRIDGE_ERROR | PROMPT_REQUIRED
 */

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

// ─── Dialog ────────────────────────────────────────────────────────────────

class AskAiDialog extends Component {
    static template = "ipai_ai_widget.AskAiDialog";
    static props = {
        close: Function,
        onInsert: { type: Function, optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.promptInput = useRef("promptInput");
        this.state = useState({
            prompt: "",
            response: null,
            error: null,
            loading: false,
        });

        onMounted(() => {
            this.promptInput.el?.focus();
        });
    }

    async onAsk() {
        const prompt = this.state.prompt.trim();
        if (!prompt || this.state.loading) return;

        this.state.loading = true;
        this.state.response = null;
        this.state.error = null;

        try {
            const result = await this.rpc("/ipai/ai/ask", { prompt });
            if (result.error) {
                this.state.error = result.error;
            } else {
                this.state.response = result;
            }
        } catch {
            this.state.error = "BRIDGE_ERROR";
        } finally {
            this.state.loading = false;
        }
    }

    onInsert() {
        if (this.state.response?.text && this.props.onInsert) {
            this.props.onInsert(this.state.response.text);
        }
        this.props.close();
    }
}

// ─── Chatter toolbar button ─────────────────────────────────────────────────

class AskAiButton extends Component {
    static template = "ipai_ai_widget.AskAiButton";
    static props = {
        composer: { optional: true },
    };

    setup() {
        this.dialog = useService("dialog");
    }

    openDialog() {
        this.dialog.add(AskAiDialog, {
            onInsert: (text) => {
                // Best-effort: attempt to append to a visible textarea/contenteditable in chatter
                const composer =
                    document.querySelector(".o_composer_text_field") ||
                    document.querySelector(".o_field_html .odoo-editor-editable");
                if (composer) {
                    if (composer.tagName === "TEXTAREA") {
                        composer.value += (composer.value ? "\n\n" : "") + text;
                        composer.dispatchEvent(new Event("input", { bubbles: true }));
                    } else {
                        const sel = window.getSelection();
                        composer.focus();
                        document.execCommand("insertText", false, text);
                        sel?.collapseToEnd();
                    }
                }
            },
        });
    }
}

// ─── Registration: inject into chatter action buttons ───────────────────────
// Odoo 19 / OWL 2: patch ChatterTopbar or register as systray/action
// For maximum compatibility, we register as a chatter action component.

registry.category("mail.chatter/action").add("ipai_ask_ai", {
    component: AskAiButton,
    props: {},
    sequence: 100,
});
