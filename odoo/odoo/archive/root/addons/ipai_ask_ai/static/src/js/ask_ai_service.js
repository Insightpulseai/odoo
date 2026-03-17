/** @odoo-module **/
/**
 * Ask AI Service
 *
 * Provides the service layer for AI chat functionality.
 * Handles communication with the backend AI endpoints.
 */

import { registry } from "@web/core/registry";

/**
 * Ask AI Service definition
 *
 * This service is registered in the services registry and provides
 * methods for interacting with the AI backend.
 */
export const askAIService = {
    dependencies: ["orm", "notification"],

    start(env, { orm, notification }) {
        let channelId = null;
        let isInitialized = false;

        return {
            /**
             * Check if the service is available
             */
            get isAvailable() {
                return true;
            },

            /**
             * Check if service is initialized
             */
            get isInitialized() {
                return isInitialized;
            },

            /**
             * Get the current channel ID
             */
            get channelId() {
                return channelId;
            },

            /**
             * Initialize the AI channel
             */
            async initialize() {
                if (isInitialized) {
                    return { id: channelId };
                }

                try {
                    const result = await this.createChannel();
                    channelId = result.id;
                    isInitialized = true;
                    return result;
                } catch (error) {
                    console.error("[AskAI] Failed to initialize:", error);
                    throw error;
                }
            },

            /**
             * Create or get the AI chat channel
             */
            async createChannel() {
                try {
                    const result = await orm.call(
                        "discuss.channel",
                        "create_ai_draft_channel",
                        []
                    );
                    channelId = result.id;
                    return result;
                } catch (error) {
                    console.error("[AskAI] Failed to create channel:", error);
                    throw error;
                }
            },

            /**
             * Send a message and get AI response
             */
            async sendMessage(messageBody, context = {}) {
                if (!channelId) {
                    await this.initialize();
                }

                try {
                    // Call the AI message endpoint
                    const result = await fetch("/ai/channel/message", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {
                                channel_id: channelId,
                                message_body: messageBody,
                                context: context,
                            },
                        }),
                    });

                    const data = await result.json();
                    return data.result;
                } catch (error) {
                    console.error("[AskAI] Failed to send message:", error);
                    notification.add("Failed to send message. Please try again.", {
                        type: "danger",
                    });
                    throw error;
                }
            },

            /**
             * Generate AI response without posting to channel
             */
            async generateResponse(messageBody, context = {}) {
                try {
                    const result = await fetch("/ai/generate_response", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {
                                message_body: messageBody,
                                context: context,
                            },
                        }),
                    });

                    const data = await result.json();
                    return data.result;
                } catch (error) {
                    console.error("[AskAI] Failed to generate response:", error);
                    throw error;
                }
            },

            /**
             * Get AI capabilities
             */
            async getCapabilities() {
                try {
                    const result = await fetch("/ai/capabilities", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {},
                        }),
                    });

                    const data = await result.json();
                    return data.result;
                } catch (error) {
                    console.error("[AskAI] Failed to get capabilities:", error);
                    return { capabilities: [] };
                }
            },

            /**
             * Get status of the AI service
             */
            getStatus() {
                return {
                    available: true,
                    initialized: isInitialized,
                    channelId: channelId,
                };
            },
        };
    },
};

// Register the service
registry.category("services").add("askAI", askAIService);
