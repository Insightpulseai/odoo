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

    setup() {
        this.state = useState({
            isOpen: false,
            messages: [],
            isLoading: false,
            error: null,
            isDisabled: false,
            pendingFiles: [],
        });
        this.inputRef = useRef("promptInput");
        this.messagesRef = useRef("messageList");
        this.fileInputRef = useRef("fileInput");
        this.action = useService("action");

        // Check if copilot is enabled via dedicated endpoint (no admin ACL needed)
        onMounted(async () => {
            try {
                const result = await rpc("/ipai/copilot/status", {});
                this.state.isDisabled = !result.enabled;
            } catch {
                this.state.isDisabled = true;
            }
        });
    }

    // Max 10 MB per file
    static MAX_FILE_SIZE = 10 * 1024 * 1024;
    static ALLOWED_TYPES = new Set([
        "application/pdf",
        "image/png", "image/jpeg", "image/gif", "image/webp",
        "text/plain", "text/csv", "text/html",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/json",
    ]);

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

    onClickAttach() {
        this.fileInputRef.el?.click();
    }

    onFileChange(ev) {
        const files = ev.target.files;
        if (!files?.length) return;

        for (const file of files) {
            if (!CopilotSystrayButton.ALLOWED_TYPES.has(file.type)) {
                this.state.error = `File type not supported: ${file.type || file.name}`;
                continue;
            }
            if (file.size > CopilotSystrayButton.MAX_FILE_SIZE) {
                this.state.error = `File too large: ${file.name} (max 10 MB)`;
                continue;
            }
            this.state.pendingFiles.push({
                file,
                name: file.name,
                mimetype: file.type,
                size: file.size,
            });
        }
        // Reset input so same file can be re-selected
        ev.target.value = "";
    }

    removePendingFile(index) {
        this.state.pendingFiles.splice(index, 1);
    }

    _fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Strip "data:...;base64," prefix
                const b64 = reader.result.split(",")[1];
                resolve(b64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    _formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    onDragOver(ev) {
        ev.preventDefault();
        ev.currentTarget.classList.add("o_ipai_copilot_dragover");
    }

    onDragLeave(ev) {
        ev.currentTarget.classList.remove("o_ipai_copilot_dragover");
    }

    onDrop(ev) {
        ev.preventDefault();
        ev.currentTarget.classList.remove("o_ipai_copilot_dragover");
        const files = ev.dataTransfer?.files;
        if (files?.length) {
            // Reuse the same validation as file input
            this.onFileChange({ target: { files, value: "" } });
        }
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
        const hasPendingFiles = this.state.pendingFiles.length > 0;
        if ((!prompt && !hasPendingFiles) || this.state.isLoading) return;

        // Build attachment list for display
        const fileNames = this.state.pendingFiles.map((f) => f.name);

        // Add user message (with attachment indicators)
        this.state.messages.push({
            role: "user",
            content: prompt || "",
            attachments: fileNames.length ? fileNames : undefined,
            timestamp: new Date().toLocaleTimeString(),
        });
        input.value = "";
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        try {
            // Convert pending files to base64
            const attachments = [];
            for (const pf of this.state.pendingFiles) {
                const data = await this._fileToBase64(pf.file);
                attachments.push({
                    name: pf.name,
                    data,
                    mimetype: pf.mimetype,
                });
            }
            this.state.pendingFiles = [];

            const context = this._getPageContext();
            const result = await rpc("/ipai/copilot/chat", {
                prompt: prompt || "",
                record_model: context.record_model,
                record_id: context.record_id,
                surface: context.surface || "erp",
                attachments,
            });

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
                    attachments: result.attachments || [],
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

    clearMessages() {
        this.state.messages = [];
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
