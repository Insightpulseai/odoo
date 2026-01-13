/** @odoo-module **/
/**
 * IPAI Copilot Hub - OWL Component
 *
 * Embeds an external Fluent UI Ops Control Room application in an iframe.
 * The hub URL is fetched from Odoo system parameters via a JSON-RPC call.
 *
 * Architecture:
 * 1. Component mounts and shows loading state
 * 2. Fetches hub config from /ipai/copilot/hub/config
 * 3. Sets iframe src to the external Fluent UI app URL
 * 4. Handles errors gracefully with user-friendly messages
 */

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

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
        });

        onMounted(() => {
            this.loadHubConfig();
            this.setupMessageListener();
        });

        onWillUnmount(() => {
            this.removeMessageListener();
        });
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

            // Append view context if provided
            if (this.props.view) {
                const url = new URL(config.url);
                url.searchParams.set("view", this.props.view);
                this.state.hubUrl = url.toString();
            }

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
