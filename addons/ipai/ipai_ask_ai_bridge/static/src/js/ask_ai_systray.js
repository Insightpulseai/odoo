/** @odoo-module **/
/**
 * Ask AI Systray Component
 *
 * A thin launcher that opens an external Ask AI / Copilot service.
 * This component does NOT implement AI logic - it only:
 * - Shows a systray icon when enabled
 * - Opens the configured external URL in a panel/popup
 *
 * All AI processing happens externally per ASK_AI_CONTRACT.md
 */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AskAiSystray extends Component {
    static template = "ipai_ask_ai_bridge.AskAiSystray";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.state = useState({
            isOpen: false,
            isLoading: false,
            endpointUrl: null,
            enabled: false,
        });
        this.loadConfig();
    }

    async loadConfig() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                model: "ir.config_parameter",
                method: "get_param",
                args: ["ipai_ask_ai_bridge.enabled"],
                kwargs: {},
            });
            this.state.enabled = result === "True";

            if (this.state.enabled) {
                const url = await this.rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["ipai_ask_ai_bridge.endpoint_url"],
                    kwargs: {},
                });
                this.state.endpointUrl = url;
            }
        } catch (e) {
            console.warn("Ask AI: Could not load config", e);
        }
    }

    async onClickAskAi() {
        if (!this.state.enabled) {
            this.notification.add("Ask AI is not enabled. Configure it in Settings.", {
                type: "warning",
            });
            return;
        }

        if (!this.state.endpointUrl) {
            this.notification.add("Ask AI endpoint URL is not configured.", {
                type: "warning",
            });
            return;
        }

        // Open external Copilot in a new window/panel
        // The external service handles all AI logic
        const tenantId = await this.rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["ipai_ask_ai_bridge.tenant_id"],
            kwargs: {},
        });

        const url = new URL(this.state.endpointUrl);
        if (tenantId) {
            url.searchParams.set("tenant", tenantId);
        }

        // Open in popup (external service)
        window.open(
            url.toString(),
            "ask_ai_copilot",
            "width=450,height=600,right=0,top=100"
        );
    }
}

AskAiSystray.props = {};

// Only register if module is loaded
export const askAiSystrayItem = {
    Component: AskAiSystray,
};

registry.category("systray").add("AskAiSystray", askAiSystrayItem, { sequence: 1 });
