/** @odoo-module */

import { registry } from "@web/core/registry";

/**
 * CopilotService — manages copilot conversation state and gateway communication.
 *
 * Registered in the service registry so any OWL component can inject it
 * via useService("copilot").
 */
const copilotService = {
    dependencies: ["rpc"],

    start(env, { rpc }) {
        let currentConversationId = null;

        /**
         * Send a message to the copilot gateway.
         *
         * @param {string} message - The user's message text
         * @param {Object} [context={}] - Optional context (context_model, context_res_id, surface)
         * @returns {Promise<Object>} Response from the gateway
         */
        async function sendMessage(message, context = {}) {
            const result = await rpc("/ipai/copilot/chat", {
                conversation_id: currentConversationId,
                message,
                context,
            });
            if (result.conversation_id) {
                currentConversationId = result.conversation_id;
            }
            return result;
        }

        /**
         * Create a new conversation.
         *
         * @param {string} [name=""] - Conversation name
         * @param {Object} [context={}] - Optional context
         * @returns {Promise<Object>} The created conversation data
         */
        async function createConversation(name = "", context = {}) {
            const result = await rpc("/ipai/copilot/conversations/create", {
                name,
                context_model: context.context_model || "",
                context_res_id: context.context_res_id || 0,
            });
            if (result.conversation_id) {
                currentConversationId = result.conversation_id;
            }
            return result;
        }

        /**
         * List the current user's conversations.
         *
         * @param {string} [state="active"] - Filter by state
         * @param {number} [limit=20] - Max results
         * @returns {Promise<Object>} Conversations list and total count
         */
        async function listConversations(state = "active", limit = 20) {
            return rpc("/ipai/copilot/conversations/list", {
                state,
                limit,
            });
        }

        /**
         * Reset current conversation (start fresh).
         */
        function resetConversation() {
            currentConversationId = null;
        }

        /**
         * Get the current conversation ID.
         *
         * @returns {number|null}
         */
        function getCurrentConversationId() {
            return currentConversationId;
        }

        /**
         * Set the current conversation ID (e.g., when resuming).
         *
         * @param {number|null} id
         */
        function setCurrentConversationId(id) {
            currentConversationId = id;
        }

        /**
         * Send a message with streaming response via SSE.
         *
         * @param {string} message - The user's message text
         * @param {Object} [context={}] - Optional context
         * @param {Function} onChunk - Called with (fullText) on each chunk
         * @returns {Promise<Object>} Final result with conversation_id, content, latency_ms
         */
        async function sendMessageStreaming(message, context = {}, onChunk = () => {}) {
            const csrfToken = odoo.csrf_token || document.cookie
                .split("; ")
                .find((c) => c.startsWith("csrf_token="))
                ?.split("=")[1] || "";

            const body = JSON.stringify({
                message,
                conversation_id: currentConversationId,
                context_model: context.context_model || "",
                context_res_id: context.context_res_id || 0,
                surface: context.surface || "erp",
                csrf_token: csrfToken,
            });

            const response = await fetch("/ipai/copilot/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body,
            });

            if (!response.ok) {
                throw new Error(`Stream request failed: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = "";
            let result = {};
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                // Keep the last incomplete line in the buffer
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === "start" && data.conversation_id) {
                            currentConversationId = data.conversation_id;
                        } else if (data.type === "chunk") {
                            fullContent = data.full_content || fullContent + (data.content || "");
                            onChunk(fullContent);
                        } else if (data.type === "done") {
                            result = {
                                conversation_id: data.conversation_id || currentConversationId,
                                content: fullContent,
                                latency_ms: data.latency_ms || 0,
                                role: "assistant",
                            };
                        } else if (data.type === "error") {
                            throw new Error(data.message || "Stream error");
                        }
                    } catch (e) {
                        if (e.message && !e.message.startsWith("Unexpected")) {
                            throw e;
                        }
                    }
                }
            }

            return result;
        }

        return {
            sendMessage,
            sendMessageStreaming,
            createConversation,
            listConversations,
            resetConversation,
            getCurrentConversationId,
            setCurrentConversationId,
        };
    },
};

registry.category("services").add("copilot", copilotService);
