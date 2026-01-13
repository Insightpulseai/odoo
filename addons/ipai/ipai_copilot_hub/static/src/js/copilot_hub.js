/** @odoo-module **/
/**
 * IPAI Copilot Hub - OWL Component
 *
 * Embeds an external Fluent UI Ops Control Room application in an iframe.
 * The hub URL is fetched from Odoo system parameters via a JSON-RPC call.
 *
 * Features:
 * - Dynamic theme synchronization (suqi/system/tbwa-dark)
 * - PostMessage communication with embedded app
 * - Bidirectional theme toggle sync
 *
 * Architecture:
 * 1. Component mounts and shows loading state
 * 2. Fetches hub config from /ipai/copilot/hub/config
 * 3. Sets iframe src to the external Fluent UI app URL
 * 4. Syncs theme state between Odoo and embedded app
 */

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// Theme constants matching React app
const UI_THEMES = ["suqi", "system", "tbwa-dark"];
const SCHEMES = ["light", "dark"];
const STORAGE_KEY = "ipai-ui-theme";
const SCHEME_KEY = "ipai-color-scheme";

export class CopilotHubMain extends Component {
    static template = "ipai_copilot_hub.Main";
    static props = {
        // Optional view context
        view: { type: String, optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");

        this.iframeRef = useRef("iframe");

        this.state = useState({
            loading: true,
            error: null,
            hubUrl: null,
            showToolbar: true,
            iframeLoaded: false,
            // Theme state
            theme: this._getStoredTheme(),
            scheme: this._getStoredScheme(),
        });

        onMounted(() => {
            this.loadHubConfig();
            this.setupMessageListener();
            this._applyThemeToDOM();
        });

        onWillUnmount(() => {
            this.removeMessageListener();
        });
    }

    /**
     * Get stored theme from localStorage or default.
     */
    _getStoredTheme() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored && UI_THEMES.includes(stored)) {
                return stored;
            }
        } catch {}
        return "suqi"; // Default theme
    }

    /**
     * Get stored scheme from localStorage or system preference.
     */
    _getStoredScheme() {
        try {
            const stored = localStorage.getItem(SCHEME_KEY);
            if (stored && SCHEMES.includes(stored)) {
                return stored;
            }
            // Check system preference
            if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
                return "dark";
            }
        } catch {}
        return "light"; // Default scheme
    }

    /**
     * Apply current theme to DOM attributes.
     */
    _applyThemeToDOM() {
        const root = document.documentElement;
        root.setAttribute("data-theme", this.state.theme);
        root.setAttribute("data-scheme", this.state.scheme);

        if (this.state.scheme === "dark") {
            root.classList.add("dark");
        } else {
            root.classList.remove("dark");
        }
    }

    /**
     * Set theme and sync with iframe.
     */
    setTheme(theme) {
        if (!UI_THEMES.includes(theme)) return;

        this.state.theme = theme;
        localStorage.setItem(STORAGE_KEY, theme);

        // Auto-set scheme for tbwa-dark
        if (theme === "tbwa-dark") {
            this.setScheme("dark");
        }

        this._applyThemeToDOM();
        this._sendThemeToHub();
    }

    /**
     * Set color scheme and sync with iframe.
     */
    setScheme(scheme) {
        if (!SCHEMES.includes(scheme)) return;

        this.state.scheme = scheme;
        localStorage.setItem(SCHEME_KEY, scheme);

        this._applyThemeToDOM();
        this._sendThemeToHub();
    }

    /**
     * Toggle between light and dark scheme.
     */
    toggleScheme() {
        this.setScheme(this.state.scheme === "light" ? "dark" : "light");
    }

    /**
     * Cycle through available themes.
     */
    cycleTheme() {
        const currentIndex = UI_THEMES.indexOf(this.state.theme);
        const nextIndex = (currentIndex + 1) % UI_THEMES.length;
        this.setTheme(UI_THEMES[nextIndex]);
    }

    /**
     * Send current theme to the hub via postMessage.
     */
    _sendThemeToHub() {
        if (!this.iframeRef.el || !this.state.hubUrl) {
            return;
        }

        try {
            const hubOrigin = new URL(this.state.hubUrl).origin;
            this.iframeRef.el.contentWindow.postMessage(
                {
                    type: "IPAI_THEME_CHANGE",
                    theme: this.state.theme,
                    scheme: this.state.scheme,
                },
                hubOrigin
            );
        } catch (error) {
            console.error("Failed to send theme to hub:", error);
        }
    }

    /**
     * Fetch hub configuration from Odoo backend.
     */
    async loadHubConfig() {
        try {
            this.state.loading = true;
            this.state.error = null;

            const config = await this.rpc("/ipai/copilot/hub/config", {});

            if (!config || !config.url) {
                throw new Error("Hub URL not configured");
            }

            this.state.hubUrl = config.url;
            this.state.showToolbar = config.show_toolbar !== false;

            // Append view context and theme params if provided
            const url = new URL(config.url);
            if (this.props.view) {
                url.searchParams.set("view", this.props.view);
            }
            // Pass initial theme via URL params
            url.searchParams.set("theme", this.state.theme);
            url.searchParams.set("scheme", this.state.scheme);
            this.state.hubUrl = url.toString();

            this.state.loading = false;

        } catch (error) {
            console.error("Failed to load Copilot Hub config:", error);
            this.state.loading = false;
            this.state.error = error.message || "Failed to load hub configuration";
        }
    }

    /**
     * Handle iframe load event.
     */
    onIframeLoad() {
        this.state.iframeLoaded = true;
        // Send theme after iframe loads
        this._sendThemeToHub();
    }

    /**
     * Handle iframe error event.
     */
    onIframeError() {
        this.state.error = "Failed to load the Ops Control Room";
        this.notification.add("Failed to load external application", {
            type: "danger",
        });
    }

    /**
     * Refresh the iframe by reloading the hub URL.
     */
    refresh() {
        if (this.iframeRef.el && this.state.hubUrl) {
            this.state.iframeLoaded = false;
            this.iframeRef.el.src = this.state.hubUrl;
        }
    }

    /**
     * Open the hub in a new window/tab.
     */
    openInNewWindow() {
        if (this.state.hubUrl) {
            window.open(this.state.hubUrl, "_blank");
        }
    }

    /**
     * Open settings dialog.
     */
    openSettings() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "copilot.hub.settings",
            views: [[false, "form"]],
            target: "new",
        });
    }

    /**
     * Setup postMessage listener for hub<->Odoo communication.
     */
    setupMessageListener() {
        this._messageHandler = (event) => {
            // Validate origin matches hub URL
            if (this.state.hubUrl) {
                try {
                    const hubOrigin = new URL(this.state.hubUrl).origin;
                    if (event.origin !== hubOrigin) {
                        return;
                    }
                } catch {
                    return;
                }
            }

            // Handle messages from the hub
            if (event.data && event.data.type) {
                this.handleHubMessage(event.data);
            }
        };

        window.addEventListener("message", this._messageHandler);
    }

    /**
     * Remove the postMessage listener.
     */
    removeMessageListener() {
        if (this._messageHandler) {
            window.removeEventListener("message", this._messageHandler);
        }
    }

    /**
     * Handle incoming messages from the hub.
     * @param {Object} message - Message data from the hub
     */
    handleHubMessage(message) {
        switch (message.type) {
            case "IPAI_THEME_SYNC":
                // Hub sends theme sync request
                if (message.theme && UI_THEMES.includes(message.theme)) {
                    this.setTheme(message.theme);
                }
                if (message.scheme && SCHEMES.includes(message.scheme)) {
                    this.setScheme(message.scheme);
                }
                break;

            case "hub:navigate":
                // Hub requests navigation to an Odoo action
                if (message.action) {
                    this.action.doAction(message.action);
                }
                break;

            case "hub:notification":
                // Hub sends a notification
                this.notification.add(message.message || "Notification", {
                    type: message.notificationType || "info",
                });
                break;

            case "hub:ready":
                // Hub signals it's ready
                this.sendContextToHub();
                this._sendThemeToHub();
                break;

            default:
                console.debug("Unknown hub message type:", message.type);
        }
    }

    /**
     * Send Odoo context to the hub via postMessage.
     */
    async sendContextToHub() {
        if (!this.iframeRef.el || !this.state.hubUrl) {
            return;
        }

        try {
            const context = await this.rpc("/ipai/copilot/hub/context", {});
            const hubOrigin = new URL(this.state.hubUrl).origin;

            this.iframeRef.el.contentWindow.postMessage(
                {
                    type: "odoo:context",
                    context: context,
                },
                hubOrigin
            );
        } catch (error) {
            console.error("Failed to send context to hub:", error);
        }
    }
}

// Register as a client action
registry.category("actions").add("ipai_copilot_hub.main", CopilotHubMain);

export default CopilotHubMain;
