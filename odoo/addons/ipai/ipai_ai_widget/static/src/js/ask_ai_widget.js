/** @odoo-module **/
/**
 * ipai_ai_widget — OWL 2 "Ask AI" component for Odoo 19 CE.
 *
 * Architecture:
 *   AskAiButton  — injected into Chatter via mail.chatter/action registry
 *     → AskAiDialog (modal)
 *       → JSON-RPC POST /ipai/ai/ask
 *         → ai_proxy.py controller
 *           → IPAI provider bridge (Gemini route)
 *
 * Record context (threadModel + threadId) flows:
 *   Chatter thread → AskAiButton props → AskAiDialog props → RPC payload
 *
 * Bridge contract:
 *   Request:  { prompt, record_model, record_id }
 *   Response: { provider, text, model, trace_id } on success
 *             { error: <CODE>, status: <int> }   on failure
 *
 * Error codes (mirrored in ai_proxy.py):
 *   BRIDGE_URL_NOT_CONFIGURED | AI_KEY_NOT_CONFIGURED
 *   BRIDGE_TIMEOUT | BRIDGE_ERROR | PROMPT_REQUIRED
 *
 * Security: Provider keys never reach the browser.
 * The Odoo controller calls the bridge server-to-server with a bearer token.
 */

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

// ── Human-readable error messages (never show error codes to users) ──────────
const ERROR_MESSAGES = {
    BRIDGE_URL_NOT_CONFIGURED:
        "AI bridge URL is not configured. Ask an admin to set it in Settings → Technical.",
    AI_KEY_NOT_CONFIGURED:
        "GEMINI_API_KEY is not set on the bridge server. Contact your administrator.",
    BRIDGE_TIMEOUT:
        "The AI bridge did not respond in time. Try again in a moment.",
    BRIDGE_ERROR:
        "An error occurred calling the AI bridge. Check the server logs.",
    PROMPT_REQUIRED:
        "Please enter a prompt before clicking Ask.",
};

// ── AskAiDialog ──────────────────────────────────────────────────────────────
/**
 * Modal: prompt textarea → response box → copy-to-clipboard.
 *
 * Props:
 *   close(Function)        — dialog service close callback (required)
 *   threadModel(String)    — e.g. "sale.order"     (optional)
 *   threadId(Number|false) — DB id of the record   (optional)
 */
class AskAiDialog extends Component {
    static template = "ipai_ai_widget.AskAiDialog";
    static props = {
        close: Function,
        threadModel: { type: String, optional: true },
        threadId: { type: [Number, Boolean], optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.promptRef = useRef("promptInput");
        this.state = useState({
            prompt: "",
            loading: false,
            error: null,     // error CODE (key of ERROR_MESSAGES) or null
            response: null,  // { provider, text, model, trace_id }
            copied: false,
        });

        onMounted(() => {
            this.promptRef.el?.focus();
        });
    }

    /** Resolve error code → human-readable string. */
    get errorMessage() {
        if (!this.state.error) return null;
        return ERROR_MESSAGES[this.state.error] || `Unexpected error: ${this.state.error}`;
    }

    async onAsk() {
        const prompt = this.state.prompt.trim();
        if (!prompt || this.state.loading) return;

        this.state.loading = true;
        this.state.error = null;
        this.state.response = null;
        this.state.copied = false;

        try {
            const result = await this.rpc("/ipai/ai/ask", {
                prompt,
                record_model: this.props.threadModel || false,
                record_id: this.props.threadId || false,
            });
            if (!result || result.error) {
                this.state.error = result?.error || "BRIDGE_ERROR";
            } else {
                this.state.response = result;
            }
        } catch (_err) {
            this.state.error = "BRIDGE_ERROR";
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Copy generated text to clipboard.
     * Shows a 2-second "Copied!" confirmation in the button label.
     * Falls back silently if the Clipboard API is unavailable
     * (user can select + copy from the response box manually).
     */
    async onInsert() {
        if (!this.state.response?.text) return;
        try {
            await navigator.clipboard.writeText(this.state.response.text);
            this.state.copied = true;
            setTimeout(() => {
                this.state.copied = false;
            }, 2000);
        } catch (_e) {
            // Clipboard API unavailable; text is selectable in the response box
        }
    }
}

// ── AskAiButton ──────────────────────────────────────────────────────────────
/**
 * The small "Ask AI" button injected into the Chatter via the
 * "mail.chatter/action" registry.
 *
 * In Odoo 17/18/19, registry entries under "mail.chatter/action" receive
 * the current thread as `this.props.thread` from the Chatter component.
 * We extract threadModel and threadId to pass record context to the dialog.
 */
class AskAiButton extends Component {
    static template = "ipai_ai_widget.AskAiButton";
    static props = {
        thread: { optional: true },  // injected by Chatter
    };

    setup() {
        this.dialogService = useService("dialog");
    }

    openDialog() {
        const thread = this.props.thread;
        this.dialogService.add(AskAiDialog, {
            threadModel: thread?.model || false,
            threadId: thread?.id || false,
        });
    }
}

// ── Register the button into the Chatter ─────────────────────────────────────
// "mail.chatter/action" is the Odoo 17/18/19 OWL-native way to add toolbar
// buttons to the Chatter without patching the component or its template.
registry.category("mail.chatter/action").add("ipai_ask_ai", {
    component: AskAiButton,
    props: {},
    sequence: 100,
});
