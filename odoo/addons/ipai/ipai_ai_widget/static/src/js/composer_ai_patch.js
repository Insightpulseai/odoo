/** @odoo-module **/
/**
 * Composer AI Patch — extends the Composer component to support AiInlinePanel rendering.
 *
 * This patch:
 *   1. Registers AiInlinePanel as a sub-component of Composer (so the template can use it)
 *   2. Adds helper methods for text insertion and panel control
 *
 * The corresponding template patch (composer_ai_patch.xml) uses t-inherit to insert
 * the AiInlinePanel DOM node between the input container and the footer.
 */

import { Composer } from "@mail/core/common/composer";
import { AiInlinePanel } from "./ai_inline_panel";
import { patch } from "@web/core/utils/patch";

// Register AiInlinePanel as a static sub-component of Composer
patch(Composer, {
    components: { ...Composer.components, AiInlinePanel },
});

// Add instance methods for AI panel interaction
patch(Composer.prototype, {
    /**
     * Thread context for AI requests — extracts model/id from the composer's thread.
     * @returns {{ model: string, id: number } | {}}
     */
    get ipaiThread() {
        // Prefer the composer's target thread (set on Discuss channels, chatter, etc.)
        const thread = this.props.composer?.targetThread || this.thread;
        if (thread) {
            return { model: thread.model, id: thread.id };
        }
        return {};
    },

    /**
     * Insert AI-generated text into the composer.
     * Handles both plain textarea and Wysiwyg editor modes.
     * @param {string} text
     */
    ipaiInsertText(text) {
        const composer = this.props.composer;
        if (!composer || !text) return;

        if (this.editor) {
            // Wysiwyg mode — use the editor's insert API
            try {
                this.editor.shared.domInsert(
                    document.createTextNode(text)
                );
            } catch {
                // Fallback: append to composerText
                const current = composer.composerText || "";
                const sep = current && !current.endsWith("\n") ? "\n" : "";
                composer.composerText = current + sep + text;
            }
        } else {
            // Plain textarea mode — append to composerText (bound via t-model)
            const current = composer.composerText || "";
            const sep = current && !current.endsWith("\n") ? "\n" : "";
            composer.composerText = current + sep + text;
        }
        // Trigger autofocus to update the textarea height
        composer.autofocus++;
    },

    /**
     * Replace selected text or insert if no selection.
     * @param {string} text
     */
    ipaiReplaceText(text) {
        // Selection-aware replace is best-effort; fallback to insert
        this.ipaiInsertText(text);
    },

    /**
     * Close the AI panel.
     */
    ipaiClosePanel() {
        if (this.ipaiAiPanel) {
            this.ipaiAiPanel.show = false;
        }
    },
});
