/** @odoo-module **/
import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { copilotState, openCopilot, closeCopilot, newChat, sendMessage } from "./copilot_store";

class CopilotPanel extends Component {
    setup() {
        this.state = copilotState;
        this.scrollArea = useRef("scrollArea");
        this.input = useRef("input");

        onMounted(() => {
            // keep panel mounted; scroll when opening or new messages
            this._scrollToBottom();
        });
    }

    get canSend() {
        return !this.state.loading && (this.state.draft || "").trim().length > 0;
    }

    _scrollToBottom() {
        const el = this.scrollArea.el;
        if (!el) return;
        requestAnimationFrame(() => {
            el.scrollTop = el.scrollHeight;
        });
    }

    close = () => closeCopilot();
    newChat = () => { newChat(); this._scrollToBottom(); };

    quickAsk = async (txt) => {
        await sendMessage(txt, this._context());
        this._scrollToBottom();
    };

    _context() {
        // Minimal now; later: inject active model/res_id, breadcrumbs, etc.
        return {};
    }

    onKeyDown = async (ev) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            await this.send();
        }
    };

    send = async () => {
        if (!this.canSend) return;
        const txt = this.state.draft;
        await sendMessage(txt, this._context());
        this._scrollToBottom();
    };
}
CopilotPanel.template = "ipai_copilot.copilot_panel_xml";

class CopilotSystray extends Component {
    setup() {
        this.state = copilotState;
    }
    toggle = () => {
        if (this.state.open) closeCopilot();
        else openCopilot();
    };
}
CopilotSystray.template = "ipai_copilot.CopilotSystray";

registry.category("systray").add("ipai_copilot.systray", {
    Component: CopilotSystray,
    sequence: 5,
});

// Mount the panel once in the DOM via a small hack: render via systray template.
registry.category("main_components").add("ipai_copilot.panel", { Component: CopilotPanel });
