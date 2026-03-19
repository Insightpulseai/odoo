/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

/**
 * Context Service - Tracks current Odoo context for AI prompts
 *
 * Captures:
 * - Current model and record
 * - Current view type
 * - Selected records (in list view)
 * - Current action
 */
export const contextService = {
    dependencies: ["router", "action"],

    start(env, { router, action }) {
        const state = reactive({
            model: null,
            resId: null,
            resIds: [],
            viewType: null,
            actionId: null,
            displayName: null,
        });

        // Listen to route changes
        router.addEventListener("router-changed", () => {
            updateFromRouter();
        });

        function updateFromRouter() {
            const currentHash = router.current.hash;
            state.model = currentHash.model || null;
            state.resId = currentHash.id ? parseInt(currentHash.id) : null;
            state.viewType = currentHash.view_type || null;
            state.actionId = currentHash.action ? parseInt(currentHash.action) : null;
        }

        // Initial update
        updateFromRouter();

        return {
            state,

            /**
             * Get current context as object
             */
            getContext() {
                return {
                    model: state.model,
                    res_id: state.resId,
                    res_ids: state.resIds,
                    view_type: state.viewType,
                    action_id: state.actionId,
                    display_name: state.displayName,
                };
            },

            /**
             * Update context from a controller/view
             */
            setContext(context) {
                if (context.model !== undefined) state.model = context.model;
                if (context.resId !== undefined) state.resId = context.resId;
                if (context.resIds !== undefined) state.resIds = context.resIds;
                if (context.viewType !== undefined) state.viewType = context.viewType;
                if (context.actionId !== undefined) state.actionId = context.actionId;
                if (context.displayName !== undefined) state.displayName = context.displayName;
            },

            /**
             * Set selected record IDs (from list view selection)
             */
            setSelectedIds(ids) {
                state.resIds = ids || [];
            },

            /**
             * Build a context description string for AI
             */
            getContextDescription() {
                const parts = [];

                if (state.model) {
                    parts.push(`Model: ${state.model}`);
                }
                if (state.resId) {
                    parts.push(`Record ID: ${state.resId}`);
                }
                if (state.displayName) {
                    parts.push(`Record: ${state.displayName}`);
                }
                if (state.viewType) {
                    parts.push(`View: ${state.viewType}`);
                }
                if (state.resIds.length > 0) {
                    parts.push(`Selected: ${state.resIds.length} records`);
                }

                return parts.join("\n");
            },

            /**
             * Check if we have a specific record context
             */
            hasRecordContext() {
                return !!(state.model && state.resId);
            },

            /**
             * Check if we have selected records
             */
            hasSelection() {
                return state.resIds.length > 0;
            },
        };
    },
};

registry.category("services").add("ask_ai_context", contextService);
