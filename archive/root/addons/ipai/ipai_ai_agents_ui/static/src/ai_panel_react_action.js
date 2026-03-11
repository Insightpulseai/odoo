/** @odoo-module */

/**
 * IPAI AI Agents - React Panel Client Action
 *
 * Odoo client action wrapper that mounts the React + Fluent UI panel.
 * The React bundle is loaded as an IIFE and exposes window.IPAI_AI_UI.mount().
 */

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

export class IPAIAIReactPanel extends Component {
    static template = "ipai_ai_agents_ui.ReactPanelContainer";
    static props = {};

    setup() {
        this.containerRef = useRef("container");
        this.unmountFn = null;

        onMounted(() => {
            this._mountReactApp();
        });

        onWillUnmount(() => {
            this._unmountReactApp();
        });
    }

    _mountReactApp() {
        const container = this.containerRef.el;
        if (!container) {
            console.error("IPAI AI: Container element not found");
            return;
        }

        // Check if React bundle is loaded
        if (!window.IPAI_AI_UI || typeof window.IPAI_AI_UI.mount !== "function") {
            console.error("IPAI AI: React bundle not loaded (ipai_ai_ui.iife.js)");
            container.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #666;">
                    <h3>AI Panel Loading Error</h3>
                    <p>The React UI bundle could not be loaded.</p>
                    <p>Please check that the module is properly installed.</p>
                </div>
            `;
            return;
        }

        // Mount React app with configuration
        this.unmountFn = window.IPAI_AI_UI.mount(container, {
            rpcRouteBootstrap: "/ipai_ai_agents/bootstrap",
            rpcRouteAsk: "/ipai_ai_agents/ask",
            rpcRouteFeedback: "/ipai_ai_agents/feedback",
        });
    }

    _unmountReactApp() {
        if (this.unmountFn && typeof this.unmountFn === "function") {
            try {
                this.unmountFn();
            } catch (e) {
                console.warn("IPAI AI: Error unmounting React app:", e);
            }
        }
    }
}

// Register as client action
registry.category("actions").add("ipai_ai_agents.ai_panel_react_action", IPAIAIReactPanel);

// Add template inline using OWL xml template
IPAIAIReactPanel.template = owl.xml`
    <div class="ipai-ai-react-container h-100 w-100" t-ref="container"></div>
`;
