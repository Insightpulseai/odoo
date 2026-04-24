/** @odoo-module **/

import { Component, useState, useService } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { PulserChatPanel } from "../chat/pulser_chat_panel";

export class PulserSystray extends Component {
    static template = "ipai_pulser_chat.Systray";
    static components = { PulserChatPanel };

    setup() {
        this.state = useState({
            isOpen: false,
        });
    }

    togglePanel() {
        this.state.isOpen = !this.state.isOpen;
    }

    closePanel() {
        this.state.isOpen = false;
    }
}

registry.category("systray").add(
    "ipai_pulser_chat.Systray",
    {
        Component: PulserSystray,
        // Always render — the panel itself shows a helpful "disabled" notice
        // when the feature is off, so users can find the settings path.
        isDisplayed: () => true,
    },
    { sequence: 15 }
);
