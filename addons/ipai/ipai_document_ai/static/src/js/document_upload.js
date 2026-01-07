/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Document Upload Widget
 *
 * Provides drag-and-drop upload functionality for documents
 * with OCR extraction.
 */
export class DocumentUploadWidget extends Component {
    static template = "ipai_document_ai.DocumentUploadWidget";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");

        this.state = useState({
            isDragging: false,
            isUploading: false,
            isProcessing: false,
            uploadProgress: 0,
            extractedData: null,
            error: null,
        });

        this.dropZoneRef = useRef("dropZone");
        this.fileInputRef = useRef("fileInput");

        onMounted(() => {
            this._setupDragAndDrop();
        });
    }

    _setupDragAndDrop() {
        const dropZone = this.dropZoneRef.el;
        if (!dropZone) return;

        ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropZone.addEventListener("dragenter", () => {
            this.state.isDragging = true;
        });

        dropZone.addEventListener("dragleave", (e) => {
            if (!dropZone.contains(e.relatedTarget)) {
                this.state.isDragging = false;
            }
        });

        dropZone.addEventListener("drop", (e) => {
            this.state.isDragging = false;
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this._handleFile(files[0]);
            }
        });
    }

    onClickUpload() {
        this.fileInputRef.el?.click();
    }

    onFileChange(ev) {
        const files = ev.target.files;
        if (files.length > 0) {
            this._handleFile(files[0]);
        }
    }

    async _handleFile(file) {
        // Validate file type
        const allowedTypes = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
        ];
        if (!allowedTypes.includes(file.type)) {
            this.notification.add(
                _t("Invalid file type. Please upload PDF or image files."),
                { type: "danger" }
            );
            return;
        }

        // Validate file size (25MB max)
        const maxSize = 25 * 1024 * 1024;
        if (file.size > maxSize) {
            this.notification.add(
                _t("File too large. Maximum size is 25MB."),
                { type: "danger" }
            );
            return;
        }

        this.state.isUploading = true;
        this.state.error = null;

        try {
            // Read file as base64
            const base64Content = await this._readFileAsBase64(file);

            // Create attachment
            const attachmentId = await this.rpc("/web/dataset/call_kw", {
                model: "ir.attachment",
                method: "create",
                args: [
                    {
                        name: file.name,
                        datas: base64Content.split(",")[1],
                        mimetype: file.type,
                    },
                ],
                kwargs: {},
            });

            this.state.isUploading = false;
            this.state.isProcessing = true;

            // Trigger OCR extraction
            const result = await this.rpc("/ipai/document_ai/upload", {
                attachment_id: attachmentId,
                res_model: this.props.resModel,
                res_id: this.props.resId,
            });

            this.state.isProcessing = false;

            if (result.success) {
                this.state.extractedData = result;
                this.notification.add(_t("Document processed successfully!"), {
                    type: "success",
                });

                // Open the document record
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "ipai.document",
                    res_id: result.document_id,
                    views: [[false, "form"]],
                    target: "current",
                });
            } else {
                this.state.error = result.error;
                this.notification.add(result.error || _t("Processing failed"), {
                    type: "danger",
                });
            }
        } catch (error) {
            this.state.isUploading = false;
            this.state.isProcessing = false;
            this.state.error = error.message;
            this.notification.add(_t("Upload failed: ") + error.message, {
                type: "danger",
            });
        }
    }

    _readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    get dropZoneClass() {
        const classes = ["o_ipai_upload_zone"];
        if (this.state.isDragging) {
            classes.push("dragover");
        }
        return classes.join(" ");
    }
}

DocumentUploadWidget.props = {
    resModel: { type: String, optional: true },
    resId: { type: Number, optional: true },
};

// Register as a client action
registry.category("actions").add("ipai_document_ai.upload_widget", DocumentUploadWidget);
