/** @odoo-module **/
/**
 * Workaround for askAI service dependency issue
 *
 * This patches the askAI service to prevent startup failures when
 * the required dependencies (rpc, user) are not available.
 */

import { registry } from "@web/core/registry";

// Check if askAI service exists and remove/patch it if it has dependency issues
const servicesRegistry = registry.category("services");

// Add a dummy askAI service that does nothing to prevent the error
try {
    // Only add if not already properly registered
    if (!servicesRegistry.contains("askAI")) {
        servicesRegistry.add("askAI", {
            dependencies: [],
            start() {
                // No-op service - provides empty implementation
                return {
                    isAvailable: false,
                    ask: async () => ({ error: "AI service not configured" }),
                };
            },
        });
    }
} catch (e) {
    console.debug("askAI service patch skipped:", e.message);
}
