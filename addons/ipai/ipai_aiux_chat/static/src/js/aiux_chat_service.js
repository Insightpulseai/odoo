/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * AIUX Chat Service (stub v0)
 *
 * Canonical mode types:
 * - 'minimize': Collapsed pill state
 * - 'popup': Floating chat window (400x500px)
 * - 'sidepanel': Docked side panel (NOT fullscreen)
 */

const AIUX_MODES = {
    MINIMIZE: 'minimize',
    POPUP: 'popup',
    SIDEPANEL: 'sidepanel',  // NOT fullscreen
};

const aiuxChatService = {
    dependencies: [],

    start() {
        console.log("[ipai_aiux_chat] AIUX Chat service initialized (stub v0)");
        console.log("[ipai_aiux_chat] Available modes:", Object.values(AIUX_MODES));

        return {
            /**
             * Current widget mode
             * @type {'minimize' | 'popup' | 'sidepanel'}
             */
            mode: AIUX_MODES.MINIMIZE,

            /**
             * Set the widget display mode
             * @param {'minimize' | 'popup' | 'sidepanel'} newMode
             */
            setMode(newMode) {
                if (!Object.values(AIUX_MODES).includes(newMode)) {
                    console.warn(`[ipai_aiux_chat] Invalid mode: ${newMode}. Use: minimize, popup, sidepanel`);
                    return;
                }
                this.mode = newMode;
                console.log(`[ipai_aiux_chat] Mode changed to: ${newMode}`);
            },

            /**
             * Get current context for AI requests
             * @returns {Object} Context object with model, res_id, view_type
             */
            getContext() {
                // Stub - will be populated from action manager
                return {
                    model: null,
                    res_id: null,
                    view_type: null,
                };
            },

            /**
             * Open the chat widget
             * @param {'minimize' | 'popup' | 'sidepanel'} mode - Optional mode override
             */
            open(mode = null) {
                if (mode) {
                    this.setMode(mode);
                }
                console.log(`[ipai_aiux_chat] Opening in ${this.mode} mode`);
                // Full implementation will mount OWL component
            },

            /**
             * Close/minimize the chat widget
             */
            close() {
                this.mode = AIUX_MODES.MINIMIZE;
                console.log("[ipai_aiux_chat] Widget minimized");
            },

            /**
             * Constants for mode types
             */
            MODES: AIUX_MODES,
        };
    },
};

registry.category("services").add("aiux_chat", aiuxChatService);

// Log successful load
console.log("[ipai_aiux_chat] Service registered");
