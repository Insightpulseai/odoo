/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ActivityTimeline } from "../activity_timeline/activity_timeline";

/**
 * PulserChatPanel — main chat interface for the Pulser copilot systray.
 *
 * Renders:
 *   - message history
 *   - activity timeline (during and after requests)
 *   - input field
 *
 * Activity model:
 *   When a request starts, the panel shows an initial "Classifying request"
 *   activity. When the response arrives, all activities from the backend
 *   replace the placeholder. Activities fade after 4 seconds.
 */
export class PulserChatPanel extends Component {
    static template = "ipai_odoo_copilot.PulserChatPanel";
    static components = { ActivityTimeline };

    setup() {
        this.rpc = useService("rpc");
        this.fileInputRef = useRef("fileInput");

        this.state = useState({
            messages: [],
            activities: [],
            isLoading: false,
            inputValue: "",
            conversationId: null,
            attachedFile: null,
        });
    }

    get hasActiveActivity() {
        return this.state.activities.some((a) => a.status === "active");
    }

    async onSendMessage() {
        const text = this.state.inputValue.trim();
        if (!text || this.state.isLoading) {
            return;
        }

        // Add user message
        this.state.messages.push({
            role: "user",
            content: text,
        });
        this.state.inputValue = "";
        this.state.isLoading = true;

        // Set initial activity placeholder
        this.state.activities = [
            {
                id: "classify",
                label: "Classifying request",
                status: "active",
            },
        ];

        // Upload attachment if present
        let uploadRef = null;
        if (this.state.attachedFile) {
            this.state.activities = [
                { id: "upload", label: `Uploading ${this.state.attachedFile.name}`, status: "active" },
            ];
            try {
                uploadRef = await this._uploadAttachment(this.state.attachedFile);
                this.state.attachedFile = null;
            } catch {
                this.state.activities = [
                    { id: "upload", label: "Upload failed", status: "error" },
                ];
                this.state.isLoading = false;
                return;
            }
            this.state.activities = [
                { id: "upload", label: `Uploaded ${uploadRef.filename}`, status: "done" },
                { id: "classify", label: "Classifying request", status: "active" },
            ];
        }

        try {
            const result = await this.rpc("/api/pulser/chat", {
                message: text,
                conversation_id: this.state.conversationId,
                context: this._buildContext(),
            });

            // Update activities from backend response
            if (result.activities && result.activities.length) {
                this.state.activities = result.activities;
            } else {
                // No activities returned — mark classify as done
                this.state.activities = [
                    {
                        id: "classify",
                        label: "Classifying request",
                        status: "done",
                    },
                    {
                        id: "respond",
                        label: "Preparing response",
                        status: "done",
                    },
                ];
            }

            // Add assistant message
            if (result.content) {
                this.state.messages.push({
                    role: "assistant",
                    content: result.content,
                    skill: result.skill,
                });
            }

            if (result.conversation_id) {
                this.state.conversationId = result.conversation_id;
            }

            // Fade activities after 4 seconds
            setTimeout(() => {
                this.state.activities = [];
            }, 4000);
        } catch (error) {
            this.state.activities = [
                {
                    id: "error",
                    label: "Connection error",
                    status: "error",
                },
            ];
            this.state.messages.push({
                role: "assistant",
                content: "Sorry, I couldn't reach the service. Please try again.",
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    onClickUpload() {
        this.fileInputRef.el?.click();
    }

    onFileSelected(ev) {
        const file = ev.target.files?.[0];
        if (!file) return;
        this.state.attachedFile = file;
        // Reset input so the same file can be re-selected
        ev.target.value = "";
    }

    onRemoveAttachment() {
        this.state.attachedFile = null;
    }

    async _uploadAttachment(file) {
        const base64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.readAsDataURL(file);
        });
        const result = await this.rpc("/api/pulser/attachments/upload", {
            filename: file.name,
            data: base64,
            mime_type: file.type || "application/octet-stream",
            conversation_id: this.state.conversationId,
        });
        return result;
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.onSendMessage();
        }
    }

    _buildContext() {
        // Gather page context if available (record model, ID, surface)
        const actionService = this.env.services?.action;
        const context = { surface: "erp" };
        if (actionService?.currentController?.action) {
            const action = actionService.currentController.action;
            if (action.res_model) {
                context.context_model = action.res_model;
            }
            if (action.res_id) {
                context.context_res_id = action.res_id;
            }
        }
        return context;
    }
}
