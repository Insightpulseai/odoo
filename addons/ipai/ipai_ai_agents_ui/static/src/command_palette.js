/** @odoo-module */

/**
 * IPAI AI Agents - Command Palette Integration
 *
 * Registers the Ask AI (Fluent UI) command in Odoo's command palette.
 * Users can press Alt+Shift+F to open the AI panel.
 */

import { registry } from "@web/core/registry";

registry.category("command_palette").add("ipai_ai_agents.open_react_panel", {
    async action(env) {
        // Open the React AI panel via client action
        await env.services.action.doAction("ipai_ai_agents_ui.action_ipai_ai_agents_panel_react");
    },
    category: "Tools",
    name: "Ask AI (Fluent UI)",
    shortcut: "Alt+Shift+F",
});
