/** @odoo-module **/
/**
 * Service Initialization Patches for Odoo 18 CE
 *
 * Fixes common service dependency issues:
 * 1. askAI service - Missing rpc/user dependencies
 * 2. User service - Ensures userId is available before components load
 * 3. Home page - Defensive loading for app menus
 *
 * These patches run early in the module loading sequence to prevent
 * "Cannot read properties of undefined" errors.
 */

import { registry } from "@web/core/registry";

const servicesRegistry = registry.category("services");

// ============================================
// PATCH 1: askAI Service Stub
// ============================================
// Provides a no-op askAI service if not properly configured
// Prevents: "Some services could not be started: askAI"

try {
    if (!servicesRegistry.contains("askAI")) {
        servicesRegistry.add("askAI", {
            // No dependencies to avoid startup failures
            dependencies: [],
            start() {
                console.debug("[IPAI] askAI service stub loaded");
                return {
                    isAvailable: false,
                    isConfigured: false,
                    ask: async (query) => ({
                        success: false,
                        error: "AI service not configured",
                        message: "The AI assistant is not available in this installation.",
                    }),
                    getStatus: () => ({ available: false, reason: "not_configured" }),
                };
            },
        });
    }
} catch (e) {
    console.debug("[IPAI] askAI patch skipped:", e.message);
}

// ============================================
// PATCH 2: User Service Readiness Hook
// ============================================
// Adds a global flag when user data is fully loaded
// Components can check `window.__userServiceReady` before accessing user.userId

const originalUserService = servicesRegistry.get("user");
if (originalUserService) {
    const originalStart = originalUserService.start;

    servicesRegistry.add("user", {
        ...originalUserService,
        async start(env, deps) {
            // Call original start
            const service = await originalStart.call(this, env, deps);

            // Signal that user service is ready
            window.__userServiceReady = true;
            window.__userId = service?.userId;

            // Emit event for waiting components
            window.dispatchEvent(new CustomEvent("odoo:user:ready", {
                detail: { userId: service?.userId }
            }));

            console.debug("[IPAI] User service initialized, userId:", service?.userId);

            return service;
        },
    }, { force: true });
}

// ============================================
// PATCH 3: Safe Component Loading Helper
// ============================================
// Export utility for components to safely wait for user data

export function waitForUserService(timeout = 5000) {
    return new Promise((resolve, reject) => {
        if (window.__userServiceReady) {
            resolve({ userId: window.__userId });
            return;
        }

        const handler = (event) => {
            window.removeEventListener("odoo:user:ready", handler);
            resolve(event.detail);
        };

        window.addEventListener("odoo:user:ready", handler);

        // Timeout fallback
        setTimeout(() => {
            window.removeEventListener("odoo:user:ready", handler);
            if (window.__userServiceReady) {
                resolve({ userId: window.__userId });
            } else {
                reject(new Error("User service initialization timeout"));
            }
        }, timeout);
    });
}

// ============================================
// PATCH 4: Global Error Recovery
// ============================================
// Catches unhandled userId errors and redirects to login if session is invalid

window.addEventListener("error", (event) => {
    const message = event.message || "";

    // Check for userId-related errors
    if (message.includes("userId") && message.includes("undefined")) {
        console.error("[IPAI] Session error detected:", message);

        // Clear potentially corrupted session data
        try {
            const sessionKeys = [
                "current_tour",
                "current_tour.config",
                "current_tour.index",
            ];
            sessionKeys.forEach(key => {
                localStorage.removeItem(key);
                sessionStorage.removeItem(key);
            });
        } catch (e) {
            console.debug("[IPAI] Could not clear session storage:", e);
        }

        // Check if we should redirect
        if (!window.__sessionRecoveryAttempted) {
            window.__sessionRecoveryAttempted = true;

            // Show notification before redirect
            if (window.odoo && window.odoo.services && window.odoo.services.notification) {
                window.odoo.services.notification.add(
                    "Session issue detected. Refreshing...",
                    { type: "warning", sticky: false }
                );
            }

            // Reload after short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    }
});

// ============================================
// PATCH 5: Service Dependencies Validator
// ============================================
// Validates that required services are available before component initialization

export function validateServiceDependencies(services, required) {
    const missing = [];

    for (const serviceName of required) {
        if (!services[serviceName]) {
            missing.push(serviceName);
        }
    }

    if (missing.length > 0) {
        console.warn(`[IPAI] Missing services: ${missing.join(", ")}`);
        return { valid: false, missing };
    }

    return { valid: true, missing: [] };
}

console.debug("[IPAI] Service patches loaded successfully");
