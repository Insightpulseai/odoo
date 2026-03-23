/** @odoo-module */

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

/**
 * CopilotService — manages copilot conversation state and gateway communication.
 *
 * Registered in the service registry so any OWL component can inject it
 * via useService("copilot").
 */
const copilotService = {
    dependencies: [],

    start(env) {
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

        return {
            sendMessage,
            createConversation,
            listConversations,
            resetConversation,
            getCurrentConversationId,
            setCurrentConversationId,
        };
    },
};

registry.category("services").add("copilot", copilotService);
