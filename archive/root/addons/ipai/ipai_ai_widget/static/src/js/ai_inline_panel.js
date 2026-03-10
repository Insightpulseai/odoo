/** @odoo-module **/
/**
 * AiInlinePanel — OWL component for inline AI results below the composer.
 *
 * Architecture:
 *   Composer toolbar (Ask AI button) → toggle panel visibility
 *     → PresetChips (quick actions) or free-form prompt input
 *       → RPC POST /ipai/ai/ask
 *         → Result area with Insert/Replace/Copy/Discard
 *
 * Multi-turn: maintains thread_id across requests for conversational context.
 *
 * Props:
 *   thread(Object)          — { model, id } from the composer owner
 *   onInsertText(Function)  — callback to insert text into the composer
 *   onReplaceText(Function) — callback to replace selected text in composer
 *   onClose(Function)       — callback to close the panel
 *   hasSelection(Boolean)   — whether composer has selected text
 *   selectedText(String)    — currently selected text in the composer
 *   chatterText(String)     — recent chatter messages for context
 */

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { PresetChips } from "./preset_chips";

const ERROR_MESSAGES = {
    BRIDGE_URL_NOT_CONFIGURED:
        "AI bridge URL is not configured. Ask an admin to set it in Settings.",
    AI_KEY_NOT_CONFIGURED:
        "AI API key is not set on the bridge server.",
    BRIDGE_TIMEOUT:
        "The AI bridge did not respond in time. Try again.",
    BRIDGE_ERROR:
        "An error occurred calling the AI bridge.",
    PROMPT_REQUIRED:
        "Please enter a prompt.",
};

export class AiInlinePanel extends Component {
    static template = "ipai_ai_widget.AiInlinePanel";
    static components = { PresetChips };
    static props = {
        thread: { type: Object, optional: true },
        onInsertText: { type: Function },
        onReplaceText: { type: Function, optional: true },
        onClose: { type: Function },
        hasSelection: { type: Boolean, optional: true },
        selectedText: { type: String, optional: true },
        chatterText: { type: String, optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.promptRef = useRef("promptInput");

        this.state = useState({
            visible: true,
            prompt: "",
            loading: false,
            error: null,
            response: null,
            copied: false,
            presets: [],
            activePreset: null,
            threadId: false,
        });

        onMounted(() => {
            console.debug("[IPAI] AiInlinePanel mounted", {
                thread: this.props.thread,
                hasRpc: !!this.rpc,
            });
            this._loadPresets();
            this._pingBackend();
            this.promptRef.el?.focus();
        });
    }

    get errorMessage() {
        if (!this.state.error) return null;
        return ERROR_MESSAGES[this.state.error] || `Unexpected error: ${this.state.error}`;
    }

    async _loadPresets() {
        try {
            const presets = await this.rpc("/ipai/ai/presets", {});
            this.state.presets = presets || [];
            console.debug("[IPAI] Presets loaded:", this.state.presets.length);
        } catch (e) {
            console.warn("[IPAI] Failed to load presets:", e);
            this.state.presets = [];
        }
    }

    async _pingBackend() {
        try {
            const result = await this.rpc("/ipai/ai/ping", {});
            if (!result.ok) {
                console.warn("[IPAI] Backend ping returned issues:", result);
            } else {
                console.debug("[IPAI] Backend ping OK:", result);
            }
        } catch (e) {
            console.warn("[IPAI] Backend ping failed:", e);
        }
    }

    async _callAi(prompt, presetKey = null) {
        this.state.loading = true;
        this.state.error = null;
        this.state.response = null;
        this.state.copied = false;

        const params = {
            prompt,
            record_model: this.props.thread?.model || false,
            record_id: this.props.thread?.id || false,
        };

        if (this.state.threadId) {
            params.thread_id = this.state.threadId;
        }
        if (presetKey) {
            params.preset_key = presetKey;
        }
        if (this.props.selectedText) {
            params.selected_text = this.props.selectedText;
        }
        if (this.props.chatterText) {
            params.chatter_text = this.props.chatterText;
        }

        try {
            const result = await this.rpc("/ipai/ai/ask", params);
            if (!result || result.error) {
                this.state.error = result?.error || "BRIDGE_ERROR";
            } else {
                this.state.response = result;
                if (result.thread_id) {
                    this.state.threadId = result.thread_id;
                }
            }
        } catch {
            this.state.error = "BRIDGE_ERROR";
        } finally {
            this.state.loading = false;
        }
    }

    onPresetSelected(preset) {
        this.state.activePreset = preset;
        this._callAi(preset.label, preset.key);
    }

    onSubmit() {
        const prompt = this.state.prompt.trim();
        if (!prompt || this.state.loading) return;
        this.state.activePreset = null;
        this._callAi(prompt);
    }

    onInputKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.onSubmit();
        }
        if (ev.key === "Escape") {
            this.onClose();
        }
    }

    onInsert() {
        if (!this.state.response?.text) return;
        this.props.onInsertText(this.state.response.text);
    }

    onReplace() {
        if (!this.state.response?.text) return;
        if (this.props.onReplaceText) {
            this.props.onReplaceText(this.state.response.text);
        }
    }

    async onCopy() {
        if (!this.state.response?.text) return;
        try {
            await navigator.clipboard.writeText(this.state.response.text);
            this.state.copied = true;
            setTimeout(() => {
                this.state.copied = false;
            }, 2000);
        } catch {
            // Clipboard API unavailable; text is selectable in the result box
        }
    }

    onDiscard() {
        this.state.response = null;
        this.state.error = null;
        this.state.activePreset = null;
        this.state.prompt = "";
        this.promptRef.el?.focus();
    }

    onClose() {
        this.state.visible = false;
        this.props.onClose();
    }
}
