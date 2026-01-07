/** @odoo-module **/
/**
 * IPAI Brand Tokens Boot
 * ======================
 * Dynamically loads brand tokens from the API and applies them as CSS variables.
 * This ensures tokens are always in sync with company configuration.
 */

import { registry } from "@web/core/registry";

const TOKENS_ENDPOINT = "/ipai/ui/tokens.json";
const CACHE_KEY = "ipai_brand_tokens";
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch brand tokens from the API with caching.
 */
async function fetchTokens() {
    // Check cache first
    const cached = sessionStorage.getItem(CACHE_KEY);
    if (cached) {
        try {
            const { tokens, timestamp } = JSON.parse(cached);
            if (Date.now() - timestamp < CACHE_TTL) {
                return tokens;
            }
        } catch (e) {
            // Cache invalid, fetch fresh
        }
    }

    try {
        const response = await fetch(TOKENS_ENDPOINT);
        if (!response.ok) {
            console.warn("[IPAI Tokens] Failed to fetch tokens:", response.status);
            return null;
        }
        const tokens = await response.json();

        // Cache tokens
        sessionStorage.setItem(
            CACHE_KEY,
            JSON.stringify({ tokens, timestamp: Date.now() })
        );

        return tokens;
    } catch (error) {
        console.warn("[IPAI Tokens] Error fetching tokens:", error);
        return null;
    }
}

/**
 * Apply tokens as CSS custom properties on :root.
 */
function applyTokens(tokens) {
    if (!tokens) return;

    const root = document.documentElement;

    // Palette
    if (tokens.palette) {
        root.style.setProperty("--tbwa-primary", tokens.palette.primary);
        root.style.setProperty("--tbwa-primary-hover", tokens.palette.primaryHover);
        root.style.setProperty("--tbwa-accent", tokens.palette.accent);
        root.style.setProperty("--tbwa-accent-hover", tokens.palette.accentHover);
        root.style.setProperty("--tbwa-success", tokens.palette.success);
        root.style.setProperty("--tbwa-warning", tokens.palette.warning);
        root.style.setProperty("--tbwa-danger", tokens.palette.danger);
        root.style.setProperty("--tbwa-info", tokens.palette.info);
    }

    // Surface
    if (tokens.surface) {
        root.style.setProperty("--tbwa-bg", tokens.surface.bg);
        root.style.setProperty("--tbwa-surface", tokens.surface.card);
        root.style.setProperty("--tbwa-surface-elevated", tokens.surface.elevated);
        root.style.setProperty("--tbwa-border", tokens.surface.border);
    }

    // Text
    if (tokens.text) {
        root.style.setProperty("--tbwa-text-primary", tokens.text.primary);
        root.style.setProperty("--tbwa-text-secondary", tokens.text.secondary);
        root.style.setProperty("--tbwa-text-on-primary", tokens.text.onPrimary);
        root.style.setProperty("--tbwa-text-on-accent", tokens.text.onAccent);
    }

    // Shape
    if (tokens.radius) {
        root.style.setProperty("--tbwa-radius-sm", tokens.radius.sm);
        root.style.setProperty("--tbwa-radius-md", tokens.radius.md);
        root.style.setProperty("--tbwa-radius-lg", tokens.radius.lg);
    }

    // Shadows
    if (tokens.shadow) {
        root.style.setProperty("--tbwa-shadow-sm", tokens.shadow.sm);
        root.style.setProperty("--tbwa-shadow-md", tokens.shadow.md);
        root.style.setProperty("--tbwa-shadow-lg", tokens.shadow.lg);
    }

    // Typography
    if (tokens.typography) {
        root.style.setProperty("--tbwa-font-family", tokens.typography.fontFamily);
    }

    // Also update IPAI alias variables for backward compat
    root.style.setProperty("--ipai-brand-primary", tokens.palette?.primary || "");
    root.style.setProperty("--ipai-brand-accent", tokens.palette?.accent || "");
    root.style.setProperty("--ipai-bg", tokens.surface?.bg || "");
    root.style.setProperty("--ipai-surface", tokens.surface?.card || "");
    root.style.setProperty("--ipai-text", tokens.text?.primary || "");
    root.style.setProperty("--ipai-text-muted", tokens.text?.secondary || "");

    console.log("[IPAI Tokens] Applied brand tokens:", tokens.meta?.preset || "custom");
}

/**
 * Initialize brand tokens on page load.
 */
async function initTokens() {
    const tokens = await fetchTokens();
    applyTokens(tokens);
}

// Register as a service that runs on startup
registry.category("services").add("ipai_brand_tokens", {
    dependencies: [],
    start() {
        initTokens();
        return {};
    },
});

// Also run immediately in case service registry hasn't initialized
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTokens);
} else {
    initTokens();
}
