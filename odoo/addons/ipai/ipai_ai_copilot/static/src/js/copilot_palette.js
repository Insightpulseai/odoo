/** @odoo-module **/
/**
 * IPAI Copilot Command Palette — Ctrl+Space quick-access overlay.
 *
 * Renders a centered modal overlay on top of any Odoo view.
 * User types a query and presses Enter → opens sidebar and sends the message.
 * Escape closes the palette without action.
 *
 * Registered as a main_components entry so it's always present.
 */
import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";

export class CopilotPalette extends Component {
    static template = "ipai_ai_copilot.CopilotPalette";
    static props = {};

    setup() {
        this.copilot = useService("ipai_copilot");
        this.localState = useState({ open: false, query: "" });
        this.inputRef = useRef("input");

        // Global Ctrl+Space hotkey — opens palette from any view
        useHotkey(
            "control+space",
            () => this.open(),
            { allowRepeat: false, global: true }
        );
    }

    open() {
        this.localState.open = true;
        this.localState.query = "";
        // Focus input after render cycle
        setTimeout(() => this.inputRef.el?.focus(), 50);
    }

    close() {
        this.localState.open = false;
        this.localState.query = "";
    }

    async submit() {
        const query = this.localState.query.trim();
        if (!query) return;
        this.close();
        // Open sidebar and send message
        this.copilot.state.open = true;
        await this.copilot.sendMessage(query);
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.submit();
        } else if (ev.key === "Escape") {
            this.close();
        }
    }

    onOverlayClick(ev) {
        // Only close if clicking the overlay backdrop (not the palette card)
        if (ev.target === ev.currentTarget) {
            this.close();
        }
    }
}

registry.category("main_components").add("ipai_copilot_palette", {
    Component: CopilotPalette,
    props: {},
});
