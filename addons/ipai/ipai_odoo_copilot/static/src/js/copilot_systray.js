/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

/**
 * CopilotSystrayButton — systray icon that opens the copilot chat panel.
 * Self-contained in ipai_odoo_copilot. No dependency on deprecated modules.
 */
export class CopilotSystrayButton extends Component {
    static template = "ipai_odoo_copilot.SystrayButton";

    static ALLOWED_TYPES = [
        "image/png", "image/jpeg", "image/webp", "image/gif",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ];
    static MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB
    static MAX_FILES = 10;

    setup() {
        this.state = useState({
            isOpen: false,
            messages: [],
            isLoading: false,
            error: null,
            isDisabled: false,
            attachments: [],
        });
        this.inputRef = useRef("promptInput");
        this.messagesRef = useRef("messageList");
        this.fileInputRef = useRef("fileInput");
        this.action = useService("action");

        // Check if copilot is enabled
        onMounted(async () => {
            try {
                let result = await rpc("/web/dataset/call_kw", {
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["ipai_copilot.enabled", "False"],
                    kwargs: {},
                });

                if (!["True", "true", "1"].includes(String(result))) {
                    result = await rpc("/web/dataset/call_kw", {
                        model: "ir.config_parameter",
                        method: "get_param",
                        args: ["ipai.copilot.enabled", "False"],
                        kwargs: {},
                    });
                }

                if (!["True", "true", "1"].includes(String(result))) {
                    result = await rpc("/web/dataset/call_kw", {
                        model: "ir.config_parameter",
                        method: "get_param",
                        args: ["ipai_odoo_copilot.foundry_enabled", "False"],
                        kwargs: {},
                    });
                }

                this.state.isDisabled = !["True", "true", "1"].includes(
                    String(result)
                );
            } catch {
                this.state.isDisabled = true;
            }
        });
    }

    togglePanel() {
        this.state.isOpen = !this.state.isOpen;
        this.state.error = null;
        if (this.state.isOpen && this.inputRef.el) {
            setTimeout(() => this.inputRef.el?.focus(), 100);
        }
    }

    closePanel() {
        this.state.isOpen = false;
    }

    /**
     * Get current page context (model, record ID, action) when available.
     */
    _getPageContext() {
        const context = {};
        try {
            const controller = this.action.currentController;
            if (controller) {
                const action = controller.action;
                if (action) {
                    context.record_model = action.res_model || null;
                    context.record_id = action.res_id || null;
                    context.surface = "erp";
                }
            }
        } catch {
            // Context capture is best-effort
        }
        return context;
    }

    async onKeyDown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            await this.sendMessage();
        }
    }

    async sendMessage() {
        const input = this.inputRef.el;
        const prompt = input?.value?.trim();
        const hasAttachments = this.state.attachments.length > 0;
        if ((!prompt && !hasAttachments) || this.state.isLoading) return;

        // Build display content for user message
        const fileNames = this.state.attachments.map((f) => f.name);
        const displayContent = fileNames.length
            ? `${prompt || ""}\n📎 ${fileNames.join(", ")}`.trim()
            : prompt;

        // Add user message
        this.state.messages.push({
            role: "user",
            content: displayContent,
            timestamp: new Date().toLocaleTimeString(),
        });
        input.value = "";
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        try {
            // Upload attachments first (if any)
            let uploadResult = null;
            if (hasAttachments) {
                uploadResult = await this._uploadAttachments();
                this.state.attachments = [];
            }

            const context = this._getPageContext();
            const rpcPayload = {
                prompt: prompt || (fileNames.length ? `Analyze the attached file(s): ${fileNames.join(", ")}` : ""),
                record_model: context.record_model,
                record_id: context.record_id,
                surface: context.surface || "erp",
            };

            // Include upload metadata in the chat request
            if (uploadResult && uploadResult.attachment_ids) {
                rpcPayload.attachment_ids = uploadResult.attachment_ids;
            }

            const result = await rpc("/ipai/copilot/chat", rpcPayload);

            if (result.blocked) {
                this.state.messages.push({
                    role: "assistant",
                    content: result.reason || "Response was blocked by safety filters.",
                    blocked: true,
                    timestamp: new Date().toLocaleTimeString(),
                });
            } else {
                this.state.messages.push({
                    role: "assistant",
                    content: result.content || "No response received.",
                    citations: result.citations || [],
                    timestamp: new Date().toLocaleTimeString(),
                });
            }
        } catch (err) {
            const msg = err.message || "Failed to reach copilot. Check Settings → Pulser.";
            this.state.error = msg;
            this.state.messages.push({
                role: "error",
                content: msg,
                timestamp: new Date().toLocaleTimeString(),
            });
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    // ------------------------------------------------------------------
    // File attachment methods
    // ------------------------------------------------------------------

    openFilePicker() {
        if (this.fileInputRef.el) {
            this.fileInputRef.el.click();
        }
    }

    onFileSelected(ev) {
        const files = Array.from(ev.target.files || []);
        for (const file of files) {
            if (this.state.attachments.length >= CopilotSystrayButton.MAX_FILES) {
                this.state.error = `Maximum ${CopilotSystrayButton.MAX_FILES} files allowed.`;
                break;
            }
            if (!CopilotSystrayButton.ALLOWED_TYPES.includes(file.type)) {
                this.state.error = `Unsupported file type: ${file.name}`;
                continue;
            }
            if (file.size > CopilotSystrayButton.MAX_FILE_SIZE) {
                this.state.error = `File too large: ${file.name} (max 50 MB)`;
                continue;
            }
            this.state.attachments.push(file);
        }
        // Reset input so re-selecting the same file works
        ev.target.value = "";
    }

    removeAttachment(index) {
        this.state.attachments.splice(index, 1);
    }

    getFileIcon(file) {
        if (!file || !file.type) return "fa fa-file-o";
        if (file.type.startsWith("image/")) return "fa fa-file-image-o";
        if (file.type === "application/pdf") return "fa fa-file-pdf-o";
        if (file.type.includes("wordprocessingml")) return "fa fa-file-word-o";
        if (file.type.includes("spreadsheetml")) return "fa fa-file-excel-o";
        return "fa fa-file-o";
    }

    async _uploadAttachments() {
        /**
         * Upload selected files to Odoo backend (which proxies to gateway).
         * Returns array of attachment metadata from the server.
         */
        if (!this.state.attachments.length) return [];

        const formData = new FormData();
        for (const file of this.state.attachments) {
            formData.append("files", file);
        }
        // CSRF token from cookie (Odoo 18 standard)
        const csrfMatch = document.cookie.match(/csrf_token=([^;]+)/);
        const csrfToken = csrfMatch ? decodeURIComponent(csrfMatch[1]) : (odoo.csrf_token || "");
        formData.append("csrf_token", csrfToken);

        const resp = await fetch("/ipai/copilot/upload", {
            method: "POST",
            body: formData,
            credentials: "same-origin",
        });
        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Upload failed (HTTP ${resp.status})`);
        }
        return resp.json();
    }

    clearMessages() {
        this.state.messages = [];
        this.state.attachments = [];
        this.state.error = null;
    }

    _scrollToBottom() {
        setTimeout(() => {
            const el = this.messagesRef.el;
            if (el) el.scrollTop = el.scrollHeight;
        }, 50);
    }
}

// Register in systray (rightmost position)
registry.category("systray").add("ipai_odoo_copilot.SystrayButton", {
    Component: CopilotSystrayButton,
    isDisplayed: () => true,
}, { sequence: 1 });
