/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

/**
 * AskAI Service - Manages AI Copilot state and API communication
 *
 * Provides:
 * - Conversation management
 * - Message sending/receiving
 * - Streaming support
 * - Action execution
 */
export const askAiService = {
    dependencies: ["rpc", "notification", "action"],

    start(env, { rpc, notification, action }) {
        // Reactive state
        const state = reactive({
            isOpen: false,
            isLoading: false,
            isStreaming: false,
            config: null,
            currentConversation: null,
            messages: [],
            mode: "ask", // ask | do | explain
            error: null,
        });

        // Load configuration
        async function loadConfig() {
            try {
                state.config = await rpc("/ask_ai/config");
            } catch (e) {
                console.error("Failed to load AI config:", e);
                state.config = { enabled: false };
            }
        }

        // Initialize
        loadConfig();

        return {
            state,

            /**
             * Toggle panel visibility
             */
            toggle() {
                state.isOpen = !state.isOpen;
                if (state.isOpen && !state.currentConversation) {
                    this.createConversation();
                }
            },

            /**
             * Open the panel
             */
            open(context = {}) {
                state.isOpen = true;
                if (!state.currentConversation) {
                    this.createConversation(context);
                }
            },

            /**
             * Close the panel
             */
            close() {
                state.isOpen = false;
            },

            /**
             * Set interaction mode
             */
            setMode(mode) {
                state.mode = mode;
            },

            /**
             * Create a new conversation
             */
            async createConversation(context = {}) {
                try {
                    const result = await rpc("/ask_ai/conversation/create", {
                        context_data: {
                            ...context,
                            mode: state.mode,
                        },
                    });
                    state.currentConversation = result;
                    state.messages = [];
                    state.error = null;
                } catch (e) {
                    console.error("Failed to create conversation:", e);
                    state.error = "Failed to start conversation";
                }
            },

            /**
             * Load an existing conversation
             */
            async loadConversation(conversationId) {
                try {
                    state.isLoading = true;
                    const result = await rpc(`/ask_ai/conversation/${conversationId}`);
                    if (result.error) {
                        throw new Error(result.error);
                    }
                    state.currentConversation = result;
                    state.messages = result.messages || [];
                    state.mode = result.mode || "ask";
                    state.error = null;
                } catch (e) {
                    console.error("Failed to load conversation:", e);
                    state.error = "Failed to load conversation";
                } finally {
                    state.isLoading = false;
                }
            },

            /**
             * Send a message to the AI
             */
            async sendMessage(prompt, context = {}) {
                if (!prompt.trim()) return;

                // Add user message immediately
                const userMessage = {
                    id: `temp-${Date.now()}`,
                    role: "user",
                    content: prompt,
                    create_date: new Date().toISOString(),
                };
                state.messages.push(userMessage);

                // Add loading message
                const loadingMessage = {
                    id: `loading-${Date.now()}`,
                    role: "assistant",
                    content: "",
                    isLoading: true,
                    create_date: new Date().toISOString(),
                };
                state.messages.push(loadingMessage);

                state.isLoading = true;
                state.error = null;

                try {
                    const result = await rpc("/ask_ai/execute", {
                        conversation_id: state.currentConversation?.id,
                        prompt,
                        context,
                        mode: state.mode,
                    });

                    // Remove loading message
                    const loadingIndex = state.messages.findIndex(
                        (m) => m.id === loadingMessage.id
                    );
                    if (loadingIndex !== -1) {
                        state.messages.splice(loadingIndex, 1);
                    }

                    if (result.error) {
                        throw new Error(result.error);
                    }

                    // Update conversation ID if new
                    if (result.conversation_id && !state.currentConversation?.id) {
                        state.currentConversation = { id: result.conversation_id };
                    }

                    // Add assistant response
                    state.messages.push(result.message);

                    return result.message;
                } catch (e) {
                    console.error("Failed to send message:", e);
                    state.error = e.message || "Failed to get AI response";

                    // Remove loading message on error
                    const loadingIndex = state.messages.findIndex(
                        (m) => m.id === loadingMessage.id
                    );
                    if (loadingIndex !== -1) {
                        state.messages.splice(loadingIndex, 1);
                    }

                    notification.add(state.error, { type: "danger" });
                    throw e;
                } finally {
                    state.isLoading = false;
                }
            },

            /**
             * Execute an action from an AI response
             */
            async executeAction(messageId, actionIndex) {
                try {
                    state.isLoading = true;

                    const result = await rpc("/ask_ai/execute_action", {
                        message_id: messageId,
                        action_index: actionIndex,
                    });

                    if (result.error) {
                        throw new Error(result.error);
                    }

                    // Handle navigation actions
                    if (result.action_type === "navigate" && result.model && result.res_id) {
                        action.doAction({
                            type: "ir.actions.act_window",
                            res_model: result.model,
                            res_id: result.res_id,
                            views: [[false, result.view_type || "form"]],
                            target: "current",
                        });
                    }

                    // Update message to mark action as executed
                    const message = state.messages.find((m) => m.id === messageId);
                    if (message) {
                        message.action_executed = true;
                    }

                    notification.add("Action executed successfully", { type: "success" });
                    return result;
                } catch (e) {
                    console.error("Failed to execute action:", e);
                    notification.add(e.message || "Failed to execute action", {
                        type: "danger",
                    });
                    throw e;
                } finally {
                    state.isLoading = false;
                }
            },

            /**
             * Clear current conversation
             */
            clearConversation() {
                state.currentConversation = null;
                state.messages = [];
                state.error = null;
            },

            /**
             * Get record context for current view
             */
            async getRecordContext(model, resId, fields = []) {
                try {
                    return await rpc("/ask_ai/context", {
                        model,
                        res_id: resId,
                        fields,
                    });
                } catch (e) {
                    console.error("Failed to get record context:", e);
                    return null;
                }
            },
        };
    },
};

registry.category("services").add("ask_ai", askAiService);
