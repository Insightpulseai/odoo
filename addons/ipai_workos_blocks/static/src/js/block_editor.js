/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Block type definitions with metadata
 */
const BLOCK_TYPES = {
    paragraph: { label: "Text", icon: "fa-paragraph", hint: "Plain text" },
    heading_1: { label: "Heading 1", icon: "fa-header", hint: "Large section heading" },
    heading_2: { label: "Heading 2", icon: "fa-header", hint: "Medium section heading" },
    heading_3: { label: "Heading 3", icon: "fa-header", hint: "Small section heading" },
    bulleted_list: { label: "Bulleted List", icon: "fa-list-ul", hint: "Create a bullet list" },
    numbered_list: { label: "Numbered List", icon: "fa-list-ol", hint: "Create a numbered list" },
    todo: { label: "To-do", icon: "fa-check-square-o", hint: "Track tasks with checkboxes" },
    toggle: { label: "Toggle", icon: "fa-caret-right", hint: "Collapsible content" },
    divider: { label: "Divider", icon: "fa-minus", hint: "Visual separator" },
    quote: { label: "Quote", icon: "fa-quote-left", hint: "Capture a quote" },
    callout: { label: "Callout", icon: "fa-info-circle", hint: "Highlight important info" },
    code: { label: "Code", icon: "fa-code", hint: "Code snippet" },
    image: { label: "Image", icon: "fa-image", hint: "Upload or embed image" },
    file: { label: "File", icon: "fa-file-o", hint: "Upload a file" },
};

/**
 * Work OS Block Editor Component
 * Provides Notion-like block editing experience
 */
export class BlockEditor extends Component {
    static template = "ipai_workos_blocks.BlockEditor";
    static props = {
        pageId: { type: Number },
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.containerRef = useRef("container");

        this.state = useState({
            blocks: [],
            selectedBlockId: null,
            showSlashMenu: false,
            slashMenuPosition: { top: 0, left: 0 },
            slashMenuFilter: "",
            loading: true,
        });

        onMounted(() => {
            this.loadBlocks();
            document.addEventListener("keydown", this.handleKeydown.bind(this));
        });

        onWillUnmount(() => {
            document.removeEventListener("keydown", this.handleKeydown.bind(this));
        });
    }

    async loadBlocks() {
        this.state.loading = true;
        try {
            const blocks = await this.orm.searchRead(
                "ipai.workos.block",
                [["page_id", "=", this.props.pageId], ["parent_block_id", "=", false]],
                ["id", "block_type", "content_json", "sequence", "is_checked", "content_html"],
                { order: "sequence, id" }
            );
            this.state.blocks = blocks;
        } finally {
            this.state.loading = false;
        }
    }

    handleKeydown(event) {
        // Handle slash command trigger
        if (event.key === "/" && !this.props.readonly) {
            this.showSlashMenu(event);
        }

        // Handle escape to close slash menu
        if (event.key === "Escape" && this.state.showSlashMenu) {
            this.hideSlashMenu();
        }

        // Handle enter in slash menu
        if (event.key === "Enter" && this.state.showSlashMenu) {
            event.preventDefault();
            this.selectSlashMenuItem();
        }
    }

    showSlashMenu(event) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            this.state.showSlashMenu = true;
            this.state.slashMenuPosition = {
                top: rect.bottom + window.scrollY + 4,
                left: rect.left + window.scrollX,
            };
            this.state.slashMenuFilter = "";
        }
    }

    hideSlashMenu() {
        this.state.showSlashMenu = false;
        this.state.slashMenuFilter = "";
    }

    getFilteredBlockTypes() {
        const filter = this.state.slashMenuFilter.toLowerCase();
        return Object.entries(BLOCK_TYPES).filter(([type, config]) =>
            config.label.toLowerCase().includes(filter) ||
            config.hint.toLowerCase().includes(filter)
        );
    }

    async selectSlashMenuItem(blockType = null) {
        if (!blockType) {
            const filtered = this.getFilteredBlockTypes();
            if (filtered.length > 0) {
                blockType = filtered[0][0];
            }
        }

        if (blockType) {
            await this.createBlock(blockType);
        }
        this.hideSlashMenu();
    }

    async createBlock(blockType, afterBlockId = null) {
        const sequence = this.getNextSequence(afterBlockId);
        const blockId = await this.orm.create("ipai.workos.block", [{
            page_id: this.props.pageId,
            block_type: blockType,
            sequence: sequence,
            content_json: JSON.stringify({ text: "" }),
        }]);
        await this.loadBlocks();
        this.state.selectedBlockId = blockId[0];
        return blockId[0];
    }

    getNextSequence(afterBlockId) {
        if (!afterBlockId) {
            return this.state.blocks.length > 0
                ? Math.max(...this.state.blocks.map(b => b.sequence)) + 10
                : 10;
        }
        const afterBlock = this.state.blocks.find(b => b.id === afterBlockId);
        const afterIndex = this.state.blocks.indexOf(afterBlock);
        const nextBlock = this.state.blocks[afterIndex + 1];
        if (nextBlock) {
            return Math.floor((afterBlock.sequence + nextBlock.sequence) / 2);
        }
        return afterBlock.sequence + 10;
    }

    async updateBlock(blockId, content) {
        await this.orm.write("ipai.workos.block", [blockId], {
            content_json: JSON.stringify(content),
        });
    }

    async deleteBlock(blockId) {
        await this.orm.unlink("ipai.workos.block", [blockId]);
        await this.loadBlocks();
    }

    async toggleTodo(blockId) {
        const block = this.state.blocks.find(b => b.id === blockId);
        if (block) {
            await this.orm.write("ipai.workos.block", [blockId], {
                is_checked: !block.is_checked,
            });
            await this.loadBlocks();
        }
    }

    selectBlock(blockId) {
        this.state.selectedBlockId = blockId;
    }

    isSelected(blockId) {
        return this.state.selectedBlockId === blockId;
    }
}

// Export for use in templates
export { BLOCK_TYPES };
