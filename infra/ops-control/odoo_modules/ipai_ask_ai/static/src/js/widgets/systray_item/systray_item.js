/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * AskAISystrayItem - Systray button to launch AI Copilot
 *
 * Features:
 * - Click to toggle panel
 * - Keyboard shortcut support
 * - Badge for notifications (future)
 */
export class AskAISystrayItem extends Component {
    static template = "ipai_ask_ai.SystrayItem";
    static props = {};

    setup() {
        this.askAi = useService("ask_ai");
        this.context = useService("ask_ai_context");
        this.hotkey = useService("hotkey");

        this.state = useState({
            isOpen: false,
        });

        // Register keyboard shortcut
        onMounted(() => {
            this.registerHotkey();
        });

        onWillUnmount(() => {
            this.unregisterHotkey();
        });
    }

    get isOpen() {
        return this.askAi.state.isOpen;
    }

    get isEnabled() {
        return this.askAi.state.config?.enabled !== false;
    }

    get buttonClass() {
        const classes = ["ipai-systray-btn"];
        if (this.isOpen) classes.push("ipai-systray-btn--active");
        return classes.join(" ");
    }

    /**
     * Toggle the copilot panel
     */
    onClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        if (!this.isEnabled) {
            return;
        }

        this.askAi.toggle();

        // Pass current context when opening
        if (this.askAi.state.isOpen) {
            this.askAi.open(this.context.getContext());
        }
    }

    /**
     * Register keyboard shortcut
     */
    registerHotkey() {
        const hotkey = this.askAi.state.config?.hotkey || "control+shift+a";
        // Convert to OWL hotkey format
        const formattedHotkey = hotkey
            .toLowerCase()
            .replace("ctrl+", "control+")
            .replace("cmd+", "meta+");

        this.hotkeyRemove = this.hotkey.add(formattedHotkey, () => {
            this.askAi.toggle();
        }, {
            global: true,
        });
    }

    /**
     * Unregister keyboard shortcut
     */
    unregisterHotkey() {
        if (this.hotkeyRemove) {
            this.hotkeyRemove();
        }
    }
}

// Register in systray
export const systrayItem = {
    Component: AskAISystrayItem,
    isDisplayed: (env) => true,
};

registry.category("systray").add("ask_ai", systrayItem, { sequence: 1 });
