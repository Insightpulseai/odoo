/** @odoo-module **/

import { Component, useState, useRef, onRendered } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class IpaiChatWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            isOpen: false,
            isTyping: false,
            messages: [
                { id: 1, role: 'assistant', text: 'Hello! I am your IPAI Odoo Copilot. How can I help you today?' }
            ]
        });
        this.chatContent = useRef("chatContent");
        this.chatInput = useRef("chatInput");

        onRendered(() => {
            if (this.chatContent.el) {
                this.chatContent.el.scrollTop = this.chatContent.el.scrollHeight;
            }
        });
    }

    _onToggleChat() {
        this.state.isOpen = !this.state.isOpen;
    }

    async _onInputKeydown(ev) {
        if (ev.key === "Enter" && ev.target.value.trim()) {
            const val = ev.target.value.trim();
            ev.target.value = "";
            this.state.messages.push({ id: Date.now(), role: 'user', text: val });
            
            this.state.isTyping = true;
            try {
                const res = await this.rpc("/web/dataset/call_kw/ipai.foundry.connector/action_chat_completion", {
                    model: 'ipai.foundry.connector',
                    method: 'action_chat_completion',
                    args: [val],
                    kwargs: {},
                });
                this.state.messages.push({ id: Date.now() + 1, role: 'assistant', text: res.response });
            } catch (e) {
                this.state.messages.push({ id: Date.now() + 1, role: 'assistant', text: "Error connecting to Foundry." });
            } finally {
                this.state.isTyping = false;
            }
        }
    }
}

IpaiChatWidget.template = "ipai_foundry.ChatWidget";
