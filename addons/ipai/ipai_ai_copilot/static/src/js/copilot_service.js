/** @odoo-module **/
/**
 * IPAI Copilot Service — shared reactive state and RPC bridge.
 *
 * Registered as "ipai_copilot" service. Consumed by:
 *   - CopilotSidebar (persistent panel)
 *   - CopilotPalette (command palette)
 *   - CopilotToggle (systray button)
 *
 * State is reactive (@odoo/owl reactive) so all components stay in sync.
 */
import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

export const copilotService = {
    name: "ipai_copilot",
    dependencies: ["rpc", "notification"],

    start(env, { rpc, notification }) {
        /** @type {import("@odoo/owl").Reactive} */
        const state = reactive({
            open: false,
            loading: false,
            /** @type {Array<{role:string, content:string, type?:string, tool_calls?:any[], tool_results_preview?:any[], dismissed?:boolean, trace_id?:string, results?:any[]}>} */
            messages: [],
            /** @type {Array<{id:number, title:string, body:string, category:string, priority:string, date:string|null, action_model:string}>} */
            insights: [],
            /** @type {number|null} */
            sessionId: null,
            /** @type {{model?:string, record_id?:number, active_ids?:number[], user_name?:string, company?:string}} */
            currentContext: {},
        });

        /**
         * Update current Odoo context (model, record_id, active_ids).
         * Called by view components when the user navigates to a new record.
         * @param {{model?:string, record_id?:number, active_ids?:number[]}} ctx
         */
        function setContext(ctx) {
            state.currentContext = ctx || {};
        }

        /**
         * Send a user message to the copilot.
         * Handles both plain text responses and tool confirmation flows.
         * @param {string} text
         */
        async function sendMessage(text) {
            const trimmed = (text || "").trim();
            if (!trimmed) return;

            state.messages.push({ role: "user", content: trimmed });
            state.loading = true;

            try {
                const result = await rpc("/ipai/copilot/chat", {
                    message: trimmed,
                    session_id: state.sessionId,
                    context: state.currentContext,
                });

                if (result.session_id) {
                    state.sessionId = result.session_id;
                }

                if (result.error) {
                    const errorMessages = {
                        BRIDGE_URL_NOT_CONFIGURED:
                            "AI bridge not configured. Set ipai_ai_copilot.bridge_url in system parameters.",
                        AI_KEY_NOT_CONFIGURED:
                            "AI API key not configured on the bridge server.",
                        BRIDGE_TIMEOUT: "AI bridge timed out. Please try again.",
                        MESSAGE_REQUIRED: "Please enter a message.",
                    };
                    notification.add(
                        errorMessages[result.error] || `Error: ${result.error}`,
                        { type: "danger" }
                    );
                    state.messages.push({
                        role: "assistant",
                        type: "error",
                        content: errorMessages[result.error] || `Error: ${result.error}`,
                    });
                    return;
                }

                if (result.type === "tool_confirmation") {
                    state.messages.push({
                        role: "assistant",
                        type: "tool_confirmation",
                        tool_calls: result.tool_calls,
                        tool_results_preview: result.tool_results_preview,
                        trace_id: result.trace_id,
                        content: "I need to take the following actions. Please confirm:",
                        dismissed: false,
                    });
                } else {
                    state.messages.push({
                        role: "assistant",
                        type: "message",
                        content: result.text || "",
                        trace_id: result.trace_id,
                        model: result.model,
                    });
                }
            } catch (err) {
                const msg = err.message || "Unknown error";
                notification.add(`Copilot error: ${msg}`, { type: "danger" });
                state.messages.push({
                    role: "assistant",
                    type: "error",
                    content: `Error: ${msg}`,
                });
            } finally {
                state.loading = false;
            }
        }

        /**
         * Execute tool calls that the user has confirmed via the confirmation dialog.
         * @param {Array<{name:string, args:object}>} toolCalls
         */
        async function confirmTools(toolCalls) {
            state.loading = true;
            try {
                const result = await rpc("/ipai/copilot/execute_tools", {
                    tool_calls: toolCalls,
                    session_id: state.sessionId,
                });

                const summary = (result.results || [])
                    .map((r) => {
                        if (r.status === "ok") return `✓ ${r.tool}`;
                        return `✗ ${r.tool}: ${r.error || "failed"}`;
                    })
                    .join(", ");

                state.messages.push({
                    role: "assistant",
                    type: "tool_result",
                    content: `Actions executed: ${summary}`,
                    results: result.results,
                });

                // Check for navigation results
                for (const r of result.results || []) {
                    if (r.status === "ok" && r.result && r.result.action === "navigate") {
                        // Dispatch navigation action to Odoo
                        env.services.action.doAction({
                            type: "ir.actions.act_window",
                            res_model: r.result.model,
                            res_id: r.result.id,
                            views: [[false, "form"]],
                        });
                    }
                }
            } catch (err) {
                notification.add(`Tool execution error: ${err.message || "unknown"}`, {
                    type: "danger",
                });
            } finally {
                state.loading = false;
            }
        }

        /**
         * Load proactive insights from the server.
         * Called on sidebar open and tab switch to "Insights".
         */
        async function loadInsights() {
            try {
                const result = await rpc("/ipai/copilot/insights", {});
                state.insights = Array.isArray(result) ? result : [];
            } catch {
                // Silently fail — insights are non-critical
                state.insights = [];
            }
        }

        /** Toggle sidebar open/closed. */
        function toggle() {
            state.open = !state.open;
            if (state.open && state.insights.length === 0) {
                loadInsights();
            }
        }

        /** Clear conversation history (client-side only). */
        function clearMessages() {
            state.messages = [];
            state.sessionId = null;
        }

        return {
            state,
            sendMessage,
            confirmTools,
            loadInsights,
            setContext,
            toggle,
            clearMessages,
        };
    },
};

registry.category("services").add("ipai_copilot", copilotService);
