/** @odoo-module **/
/**
 * Ask AI Systray Item
 *
 * Adds the Ask AI button to the system tray (top right)
 * and manages the chat panel visibility.
 */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { AskAIChat } from "./ask_ai_chat";

/**
 * AskAISystray - Systray button component
 */
export class AskAISystray extends Component {
    static template = "ipai_ask_ai.Systray";
    static components = { AskAIChat };
    static props = {};

    setup() {
        this.state = useState({
            showPanel: false,
            hasNotification: false,
        });

        // Global keyboard shortcut listener
        this.boundKeyHandler = this.handleKeydown.bind(this);
        document.addEventListener("keydown", this.boundKeyHandler);
    }

    /**
     * Handle global keyboard shortcuts
     */
    handleKeydown(e) {
        // Ctrl/Cmd + Shift + A to toggle Ask AI
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "a") {
            e.preventDefault();
            this.togglePanel();
        }
    }

    /**
     * Toggle the chat panel
     */
    togglePanel() {
        this.state.showPanel = !this.state.showPanel;
        if (this.state.showPanel) {
            this.state.hasNotification = false;
        }
    }

    /**
     * Close the chat panel
     */
    closePanel() {
        this.state.showPanel = false;
    }

    /**
     * Handle panel minimize
     */
    onMinimize(isMinimized) {
        // Can add minimize logic here if needed
    }

    /**
     * Cleanup on destroy
     */
    willUnmount() {
        document.removeEventListener("keydown", this.boundKeyHandler);
    }
}

// Register in systray
registry.category("systray").add("ipai_ask_ai.Systray", {
    Component: AskAISystray,
    sequence: 5, // Before other systray items
});
